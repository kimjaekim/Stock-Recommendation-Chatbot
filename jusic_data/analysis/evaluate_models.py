import warnings
warnings.filterwarnings('ignore')

import json
import pickle
import sys
from pathlib import Path
from datetime import datetime

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score

# 루트 디렉토리를 sys.path에 추가
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from utils.stock_name_mapping import STOCK_NAME_MAPPING
from utils.data_utils import load_or_download_macro_data, merge_macro_features

try:
    from utils.data_utils import merge_pykrx_features as _merge_pykrx
except Exception:
    _merge_pykrx = None

# ----------------------------- 설정 -----------------------------
PKL_PATH = ROOT_DIR / 'core' / 'final_multi_timeframe_models.pkl'
PYKRX_CACHE = ROOT_DIR / 'data' / 'pykrx_data_30stocks_cache.pkl'
REPORT_JSON = ROOT_DIR / 'reports' / 'model_performance_report.json'
REPORT_CSV = ROOT_DIR / 'reports' / 'model_performance_report.csv'
HISTORY_DIR = ROOT_DIR / 'reports' / 'perf_history'
HISTORY_DIR.mkdir(parents=True, exist_ok=True)

TASKS = ['direction', 'volatility', 'risk']
HORIZONS = ['1day', '3day', '5day', '10day']
H2N = {'1day': 1, '3day': 3, '5day': 5, '10day': 10}

# 각 과제별 데이터 수집 기간(대략적)
PERIODS = {
    'direction': '6y',
    'volatility': '2y',
    'risk': '5y',
}

# ---------------------- 보조 함수 ----------------------

def yf_download_retry(ticker: str, period: str, tries: int = 3):
    last_exc = None
    for _ in range(tries):
        try:
            df = yf.download(ticker, period=period, progress=False)
            if not df.empty:
                return df
        except Exception as e:
            last_exc = e
    if last_exc:
        print(f"[WARN] yfinance 실패: {ticker} ({last_exc})")
    return pd.DataFrame()

# ---------------------- 피처/타깃 생성 함수 ----------------------

def calc_technical_indicators(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['MA_5'] = df['Close'].rolling(5).mean()
    df['MA_20'] = df['Close'].rolling(20).mean()
    df['MA_Ratio'] = df['MA_5'] / df['MA_20']

    delta = df['Close'].diff()
    gain = (delta.where(delta > 0, 0)).rolling(14).mean()
    loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
    rs = gain / loss
    df['RSI'] = 100 - (100 / (1 + rs))

    df['Price_Change'] = df['Close'].pct_change()
    df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
    df['Volatility'] = df['Close'].pct_change().rolling(10).std()

    exp1 = df['Close'].ewm(span=12).mean()
    exp2 = df['Close'].ewm(span=26).mean()
    df['MACD'] = exp1 - exp2

    bb_middle = df['Close'].rolling(20).mean()
    bb_std = df['Close'].rolling(20).std()
    df['BB_Upper'] = bb_middle + (bb_std * 2)
    df['BB_Lower'] = bb_middle - (bb_std * 2)
    df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])

    df['Momentum_5'] = df['Close'].pct_change(5)
    return df


def add_interactions(df: pd.DataFrame) -> pd.DataFrame:
    df = df.copy()
    df['RSI_x_Volume'] = df['RSI'] * df['Volume_Ratio']
    df['Trend_Strength'] = df['MA_Ratio'] * df['Momentum_5']
    df['BB_Momentum'] = df['BB_Position'] * df['Momentum_5']
    df['Volatility_x_RSI'] = df['Volatility'] * df['RSI']
    df['MACD_x_Volume'] = df['MACD'] * df['Volume_Ratio']
    df['Price_Momentum'] = df['Price_Change'] * df['Momentum_5']
    df['RSI_MACD'] = df['RSI'] * df['MACD']
    df['BB_Volatility'] = df['BB_Position'] * df['Volatility']
    return df


def create_targets(df: pd.DataFrame, task: str, horizon_n: int, dir_median: float | None) -> pd.Series:
    df = df.copy()
    if task == 'direction':
        ret = df['Close'].pct_change(horizon_n).shift(-horizon_n)
        threshold = dir_median if dir_median is not None else ret.median(skipna=True)
        y = (ret > threshold).astype(int)
    elif task == 'volatility':
        future_vol = df['Close'].pct_change().rolling(horizon_n).std().shift(-horizon_n)
        y = (future_vol > df['Volatility']).astype(int)
    else:  # risk
        future_min = df['Close'].rolling(horizon_n).min().shift(-horizon_n)
        max_loss = (future_min - df['Close']) / df['Close']
        y = (max_loss < -0.03).astype(int)
    y.name = 'Target'
    return y

# ---------------------- 데이터셋 구축 ----------------------

def build_dataset(tickers, task, horizon, macro_df, medians, pykrx_cache) -> pd.DataFrame:
    period = PERIODS[task]
    n = H2N[horizon]
    rows = []
    dir_median = None
    if task == 'direction' and isinstance(medians, dict):
        dir_median = medians.get(f'direction_{horizon}')

    for ticker in tickers:
        try:
            data = yf_download_retry(ticker, period)
            if data.empty:
                continue
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            df = calc_technical_indicators(data)
            df = merge_macro_features(df, macro_df)

            # pykrx 병합
            if task == 'volatility':
                if _merge_pykrx and pykrx_cache and ticker in pykrx_cache:
                    df = _merge_pykrx(df, pykrx_cache, ticker)
                else:
                    df['Institution_Ratio'] = 0.33
                    df['Foreign_Ratio'] = 0.33
                    df['Individual_Ratio'] = 0.34

            df = add_interactions(df)
            df = df.replace([np.inf, -np.inf], np.nan).fillna(method='ffill').fillna(method='bfill')

            y = create_targets(df, task, n, dir_median)

            if task == 'direction':
                X = df[['MA_Ratio','RSI','Price_Change','Volume_Ratio','Volatility',
                        'MACD','BB_Position','Momentum_5',
                        'KOSPI_Change','USD_KRW_Change','VIX','VIX_Change','SP500_Change']].copy()
            elif task == 'volatility':
                X = df[['MA_Ratio','RSI','Price_Change','Volume_Ratio','Volatility',
                        'Institution_Ratio','Foreign_Ratio','Individual_Ratio']].copy()
            else:
                X = df[['MA_Ratio','RSI','Price_Change','Volume_Ratio','Volatility',
                        'MACD','BB_Position','Momentum_5',
                        'RSI_x_Volume','Trend_Strength','BB_Momentum','Volatility_x_RSI',
                        'MACD_x_Volume','Price_Momentum','RSI_MACD','BB_Volatility']].copy()

            tmp = pd.DataFrame({'Date': df.index, 'Ticker': ticker})
            y = y.reset_index(drop=True)
            ds = pd.concat([tmp.reset_index(drop=True), X.reset_index(drop=True), y], axis=1)
            if 'Target' not in ds.columns:
                continue
            ds = ds.dropna(subset=[c for c in ds.columns if c not in ['Date','Ticker']])
            rows.append(ds)
        except Exception as e:
            print(f"[WARN] build_dataset 실패: {ticker} ({e})")
            continue
    if not rows:
        return pd.DataFrame()
    data = pd.concat(rows, ignore_index=True)
    data = data.sort_values('Date')
    if 'Target' in data.columns:
        data['Target'] = data['Target'].astype(int)
    return data

# ---------------------- 분할/평가 ----------------------

def time_split(df: pd.DataFrame, target_col='Target'):
    if df.empty or target_col not in df.columns:
        return None
    df = df.sort_values('Date')
    n = len(df)
    i1 = int(n * 0.6)
    i2 = int(n * 0.8)
    train = df.iloc[:i1]
    val = df.iloc[i1:i2]
    test = df.iloc[i2:]
    def pack(split):
        X = split.drop(columns=['Date','Ticker',target_col]).values
        y = split[target_col].values
        return X, y, len(split), float(np.mean(y)) if len(y) else None
    return pack(train), pack(val), pack(test)


def compute_metrics(y_true, pred, proba):
    acc = float(accuracy_score(y_true, pred))
    f1 = float(f1_score(y_true, pred, zero_division=0))
    try:
        auc = float(roc_auc_score(y_true, proba)) if proba is not None else None
    except Exception:
        auc = None
    return acc, f1, auc


def evaluate_one(models, scalers, pcas, task, horizon, dataset):
    key = f'{task}_{horizon}'
    if dataset is None:
        return None
    (Xtr,ytr,ntr,pos_tr),(Xv,yv,nv,pos_v),(Xte,yte,nte,pos_te) = dataset

    scaler = scalers.get(key)
    def trans(X):
        Xs = scaler.transform(X) if scaler is not None else X
        p = pcas.get(key)
        return p.transform(Xs) if p is not None else Xs

    clf = models[key]

    Xtr_f, Xv_f, Xte_f = trans(Xtr), trans(Xv), trans(Xte)

    proba_tr = clf.predict_proba(Xtr_f)[:,1] if hasattr(clf,'predict_proba') else None
    pred_tr = clf.predict(Xtr_f)
    acc_tr, f1_tr, auc_tr = compute_metrics(ytr, pred_tr, proba_tr)

    proba_v = clf.predict_proba(Xv_f)[:,1] if hasattr(clf,'predict_proba') else None
    pred_v = clf.predict(Xv_f)
    acc_v, f1_v, auc_v = compute_metrics(yv, pred_v, proba_v)

    proba_te = clf.predict_proba(Xte_f)[:,1] if hasattr(clf,'predict_proba') else None
    pred_te = clf.predict(Xte_f)
    acc_te, f1_te, auc_te = compute_metrics(yte, pred_te, proba_te)

    return {
        'train_acc': acc_tr, 'train_f1': f1_tr, 'train_auc': auc_tr, 'train_n': ntr, 'train_pos_rate': pos_tr,
        'val_acc': acc_v, 'val_f1': f1_v, 'val_auc': auc_v, 'val_n': nv, 'val_pos_rate': pos_v,
        'test_acc': acc_te, 'test_f1': f1_te, 'test_auc': auc_te, 'test_n': nte, 'test_pos_rate': pos_te,
    }

# ---------------------- 메인 ----------------------

def main():
    if not PKL_PATH.exists():
        print(f'❌ PKL 없음: {PKL_PATH}')
        return

    with PKL_PATH.open('rb') as f:
        bundle = pickle.load(f)

    models = bundle['models']
    scalers = bundle.get('scalers', {})
    pcas = bundle.get('pcas', {})
    medians = bundle.get('medians', {})

    macro_df = load_or_download_macro_data()

    # pykrx 캐시 로드
    pykrx_cache = None
    if PYKRX_CACHE.exists():
        try:
            with PYKRX_CACHE.open('rb') as f:
                pykrx_cache = pickle.load(f).get('data', {})
        except Exception as e:
            print(f"[WARN] pykrx 캐시 로드 실패: {e}")
            pykrx_cache = None

    tickers = list(STOCK_NAME_MAPPING.keys())

    rows = []
    for task in TASKS:
        for hz in HORIZONS:
            df = build_dataset(tickers, task, hz, macro_df, medians, pykrx_cache)
            split = time_split(df)
            metrics = evaluate_one(models, scalers, pcas, task, hz, split)
            if metrics is None:
                rows.append({'task': task, 'horizon': hz})
                print(f"- {task:10s} {hz:5s} | 데이터 부족")
                continue
            out = {'task': task, 'horizon': hz, **metrics}
            rows.append(out)
            print(f"- {task:10s} {hz:5s} | train_acc={metrics['train_acc']} val_acc={metrics['val_acc']} test_acc={metrics['test_acc']}")

    ts = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    report = {'timestamp': ts.replace('_',' '), 'rows': rows}
    REPORT_JSON.write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    pd.DataFrame(rows).to_csv(REPORT_CSV, index=False)
    (HISTORY_DIR / f'model_performance_{ts}.json').write_text(json.dumps(report, ensure_ascii=False, indent=2), encoding='utf-8')
    pd.DataFrame(rows).to_csv(HISTORY_DIR / f'model_performance_{ts}.csv', index=False)
    print(f"\n✅ 저장: {REPORT_JSON.name}, {REPORT_CSV.name} (+ perf_history/*)")


if __name__ == '__main__':
    main()
