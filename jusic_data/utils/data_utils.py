"""
데이터 수집 및 캐싱 유틸리티

거시경제 데이터 (yfinance):
- KOSPI, USD/KRW, VIX, S&P 500

외국인/기관 데이터 (pykrx):
- 외국인/기관/개인 순매수
"""

import os
import pickle
import time
from datetime import datetime, timedelta
import pandas as pd
import yfinance as yf
from pykrx import stock
import warnings
warnings.filterwarnings('ignore')


def load_or_download_macro_data(start_date='20190101', end_date='20241231', force_refresh=False):
    """
    거시경제 데이터 로드 (캐시 우선)
    
    Args:
        start_date: 시작일 (YYYYMMDD)
        end_date: 종료일 (YYYYMMDD)
        force_refresh: 강제 새로고침
    
    Returns:
        dict: {날짜: {kospi, usd_krw, vix, sp500}}
    """
    # 루트 디렉토리 기준으로 캐시 경로 설정
    from pathlib import Path
    ROOT_DIR = Path(__file__).parent.parent
    cache_file = ROOT_DIR / 'cached_data' / 'macro_data.pkl'
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 캐시 확인
    if cache_file.exists() and not force_refresh:
        # 1일 이내면 캐시 사용
        cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - cache_time < timedelta(days=1):
            print("[Cache] Cached macro data loaded")
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
    
    # 새로 다운로드
    print("[Download] Downloading macro data (2-3 min)...")
    
    # 날짜 변환
    start = pd.to_datetime(start_date).strftime('%Y-%m-%d')
    end = pd.to_datetime(end_date).strftime('%Y-%m-%d')
    
    macro_data = {}
    
    try:
        # 1. KOSPI 지수
        print("  [1/4] KOSPI downloading...")
        kospi = yf.download('^KS11', start=start, end=end, progress=False)
        if not kospi.empty:
            if isinstance(kospi.columns, pd.MultiIndex):
                kospi.columns = kospi.columns.droplevel(1)
            macro_data['kospi'] = kospi
            print(f"     OK: KOSPI {len(kospi)} days")
        
        # 2. USD/KRW 환율
        print("  [2/4] USD/KRW downloading...")
        usd_krw = yf.download('KRW=X', start=start, end=end, progress=False)
        if not usd_krw.empty:
            if isinstance(usd_krw.columns, pd.MultiIndex):
                usd_krw.columns = usd_krw.columns.droplevel(1)
            macro_data['usd_krw'] = usd_krw
            print(f"     OK: USD/KRW {len(usd_krw)} days")
        
        # 3. VIX (변동성 지수)
        print("  [3/4] VIX downloading...")
        vix = yf.download('^VIX', start=start, end=end, progress=False)
        if not vix.empty:
            if isinstance(vix.columns, pd.MultiIndex):
                vix.columns = vix.columns.droplevel(1)
            macro_data['vix'] = vix
            print(f"     OK: VIX {len(vix)} days")
        
        # 4. S&P 500
        print("  [4/4] S&P 500 downloading...")
        sp500 = yf.download('^GSPC', start=start, end=end, progress=False)
        if not sp500.empty:
            if isinstance(sp500.columns, pd.MultiIndex):
                sp500.columns = sp500.columns.droplevel(1)
            macro_data['sp500'] = sp500
            print(f"     OK: S&P 500 {len(sp500)} days")
        
        # 캐시 저장
        with open(cache_file, 'wb') as f:
            pickle.dump(macro_data, f)
        
        print("  [Save] Cache saved")
        
    except Exception as e:
        print(f"  ERROR: Download failed: {e}")
        macro_data = {}
    
    return macro_data


def load_or_download_pykrx_data(tickers, start_date='20190101', end_date='20241231', force_refresh=False):
    """
    pykrx 데이터 로드 (캐시 우선)
    
    Args:
        tickers: 종목 티커 리스트
        start_date: 시작일 (YYYYMMDD)
        end_date: 종료일 (YYYYMMDD)
        force_refresh: 강제 새로고침
    
    Returns:
        dict: {티커: DataFrame(날짜, 기관, 외국인, 개인)}
    """
    # 루트 디렉토리 기준으로 캐시 경로 설정
    ROOT_DIR = Path(__file__).parent.parent
    cache_file = ROOT_DIR / 'cached_data' / 'pykrx_data.pkl'
    cache_file.parent.mkdir(parents=True, exist_ok=True)
    
    # 캐시 확인
    if cache_file.exists() and not force_refresh:
        # 1일 이내면 캐시 사용
        cache_time = datetime.fromtimestamp(cache_file.stat().st_mtime)
        if datetime.now() - cache_time < timedelta(days=1):
            print("[Cache] Cached pykrx data loaded")
            with open(cache_file, 'rb') as f:
                return pickle.load(f)
    
    # 새로 다운로드
    print(f"[Download] Downloading pykrx data ({len(tickers)} stocks, 5-10 min)...")
    
    pykrx_data = {}
    
    for i, ticker in enumerate(tickers, 1):
        try:
            print(f"  [{i}/{len(tickers)}] {ticker} downloading...")
            
            # 투자자별 거래 데이터 (날짜별)
            # 옵션: by="BUY" 또는 "SELL" 또는 "NET" (순매수)
            df = stock.get_market_trading_value_by_date(
                start_date, end_date, ticker, detail=True
            )
            
            if df is not None and not df.empty:
                # 컬럼명 변경 (기관, 외국인, 개인 -> 비율 계산용)
                pykrx_data[ticker] = df
                print(f"     OK: {len(df)} days")
            else:
                print(f"     WARNING: No data")
            
            # API 제한 방지 (1초 대기)
            time.sleep(1)
            
        except Exception as e:
            print(f"     ERROR: {e}")
            continue
    
    # 캐시 저장
    with open(cache_file, 'wb') as f:
        pickle.dump(pykrx_data, f)
    
    print(f"  [Save] Cache saved ({len(pykrx_data)} stocks)")
    
    return pykrx_data


def merge_macro_features(stock_df, macro_data):
    """
    주가 데이터에 거시경제 피처 추가
    
    Args:
        stock_df: 주가 데이터 DataFrame (index=날짜)
        macro_data: 거시경제 데이터 dict
    
    Returns:
        DataFrame: 거시경제 피처가 추가된 데이터
    """
    df = stock_df.copy()
    
    try:
        # KOSPI 변화율
        if 'kospi' in macro_data:
            kospi = macro_data['kospi'][['Close']].copy()
            kospi.columns = ['KOSPI']
            kospi['KOSPI_Change'] = kospi['KOSPI'].pct_change()
            df = df.join(kospi[['KOSPI_Change']], how='left')
        
        # USD/KRW 변화율
        if 'usd_krw' in macro_data:
            usd_krw = macro_data['usd_krw'][['Close']].copy()
            usd_krw.columns = ['USD_KRW']
            usd_krw['USD_KRW_Change'] = usd_krw['USD_KRW'].pct_change()
            df = df.join(usd_krw[['USD_KRW_Change']], how='left')
        
        # VIX
        if 'vix' in macro_data:
            vix = macro_data['vix'][['Close']].copy()
            vix.columns = ['VIX']
            vix['VIX_Change'] = vix['VIX'].pct_change()
            df = df.join(vix[['VIX', 'VIX_Change']], how='left')
        
        # S&P 500 변화율
        if 'sp500' in macro_data:
            sp500 = macro_data['sp500'][['Close']].copy()
            sp500.columns = ['SP500']
            sp500['SP500_Change'] = sp500['SP500'].pct_change()
            df = df.join(sp500[['SP500_Change']], how='left')
        
        # Forward fill (주말/공휴일 채우기)
        df = df.ffill()
        
    except Exception as e:
        print(f"  WARNING: Failed to add macro features: {e}")
    
    return df


def merge_pykrx_features(stock_df, pykrx_data, ticker):
    """
    주가 데이터에 pykrx 피처 추가
    
    Args:
        stock_df: 주가 데이터 DataFrame (index=날짜)
        pykrx_data: pykrx 데이터 dict
        ticker: 종목 티커
    
    Returns:
        DataFrame: pykrx 피처가 추가된 데이터
    """
    df = stock_df.copy()
    
    try:
        if ticker in pykrx_data:
            investor_df = pykrx_data[ticker].copy()
            
            # pykrx는 12개 컬럼 반환:
            # [금융투자, 보험, 투신, 사모펀드, 은행, 기타금융, 연기금, 기타법인, 개인, 외국인, 기타외국인, 전체]
            # 컬럼 위치로 접근 (한글 인코딩 문제 회피)
            cols = list(investor_df.columns)
            
            if len(cols) >= 12:
                # 기관 = 처음 8개 컬럼 합 (금융투자~기타법인)
                institution_net = investor_df.iloc[:, 0:8].sum(axis=1)
                
                # 개인 = 9번째 컬럼
                individual_net = investor_df.iloc[:, 8]
                
                # 외국인 = 10, 11번째 컬럼 합
                foreign_net = investor_df.iloc[:, 9:11].sum(axis=1)
                
                # 총 순매수 절대값 (정규화용)
                total_net = (
                    institution_net.abs() + 
                    foreign_net.abs() + 
                    individual_net.abs() + 1
                )
                
                # 순매수 비율 계산
                investor_df['Institution_Ratio'] = institution_net / total_net
                investor_df['Foreign_Ratio'] = foreign_net / total_net
                investor_df['Individual_Ratio'] = individual_net / total_net
                
                # Merge (날짜 기준)
                df = df.join(
                    investor_df[['Institution_Ratio', 'Foreign_Ratio', 'Individual_Ratio']], 
                    how='left'
                )
                
                # Forward fill (주말/공휴일)
                df = df.ffill()
            else:
                print(f"  WARNING: pykrx unexpected columns for {ticker}: {len(cols)} columns")
    
    except Exception as e:
        print(f"  WARNING: Failed to add pykrx features ({ticker}): {e}")
    
    return df


if __name__ == '__main__':
    # 테스트
    print("=" * 80)
    print("Data Utility Test")
    print("=" * 80)
    
    # 1. 거시경제 데이터
    macro = load_or_download_macro_data()
    print(f"\nMacro data: {list(macro.keys())}")
    
    # 2. pykrx 데이터 (샘플 5개)
    sample_tickers = ['005930', '000660', '051910', '035420', '035720']
    pykrx = load_or_download_pykrx_data(sample_tickers)
    print(f"\npykrx data: {list(pykrx.keys())}")
    
    print("\n[OK] Test Complete!")

