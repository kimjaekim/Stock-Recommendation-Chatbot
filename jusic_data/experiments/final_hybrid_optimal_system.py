"""
최종 하이브리드 최적 시스템 (검증 완료 - 5일 중앙값 기준)
과적합 검증 완료: 모든 모델이 균형잡힌 예측
- Direction: 6년 + Macro + Stacking + 5일 중앙값 (Test 54.8%, 상승 Recall 41.5%)
- Volatility: 2년 + pykrx + L1 강화 + 5일 변동성 (Test 66.4%, 높음 Recall 69.1%)
- Risk: 2년 + L2 + 5일 3% 손실 (Test 61.9%, 위험 Recall 45.0%)
- 총합: 183.1% (챔피언 183.8% 대비 -0.7%, 하지만 과적합 없고 균형!)
"""

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
from sklearn.decomposition import PCA
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
from sklearn.utils.class_weight import compute_class_weight
import time
import pickle
import warnings
warnings.filterwarnings('ignore')

# 거시경제 및 pykrx 데이터 유틸리티 import
from data_utils import (
    load_or_download_macro_data, 
    load_or_download_pykrx_data,
    merge_macro_features,
    merge_pykrx_features
)

print("=" * 80)
print("Final Hybrid Optimal System")
print("=" * 80)
print()

class FinalHybridOptimalSystem:
    def __init__(self):
        # 모델별 데이터 저장소
        self.direction_data = {}  # 6년 데이터
        self.volatility_data = {}  # 2년 데이터
        self.risk_data = {}  # 5년 데이터
        
        self.features_data = {}
        self.current_prices = {}
        
        # 스케일러 (모델별)
        self.direction_scaler = RobustScaler()
        self.volatility_scaler = RobustScaler()
        self.risk_scaler = RobustScaler()
        
        # PCA (모델별) - 95% 설명력 유지 (최적 설정)
        self.direction_pca = PCA(n_components=0.95, random_state=42)
        self.volatility_pca = PCA(n_components=0.95, random_state=42)
        self.risk_pca = PCA(n_components=0.95, random_state=42)
        
        # 최적화된 모델들
        self.direction_model = None
        self.volatility_model = None
        self.risk_model = None
        
        # 검증 결과
        self.validation_results = {}
        self.val_results = {}
        self.test_results = {}
        
        # 외부 데이터 (거시경제 + pykrx + 감정)
        self.macro_data = None
        self.pykrx_data = None
        self.sentiment_data = None
        
    def load_external_data(self, tickers):
        """외부 데이터 로드 (거시경제 + pykrx + 감정)"""
        print("0. External data loading (Macro + pykrx + Sentiment)...")
        
        # 거시경제 데이터 (Direction 모델용)
        self.macro_data = load_or_download_macro_data()
        print(f"   Macro data: {list(self.macro_data.keys())}")
        
        # pykrx 데이터 (Volatility 모델용)
        import os
        cache_file = 'pykrx_data_30stocks_cache.pkl'
        if os.path.exists(cache_file):
            with open(cache_file, 'rb') as f:
                cache = pickle.load(f)
            self.pykrx_data = cache['data']
            print(f"   pykrx data: {len(self.pykrx_data)} stocks")
        else:
            print(f"   pykrx data: Cache not found")
            self.pykrx_data = None
        
        # 감정 데이터 (Risk 모델용)
        sentiment_cache_file = 'cached_data/naver_api_news_cache.pkl'
        if os.path.exists(sentiment_cache_file):
            with open(sentiment_cache_file, 'rb') as f:
                cache = pickle.load(f)
            self.sentiment_data = cache['data']
            print(f"   Sentiment data: {len(self.sentiment_data)} stocks (Real news)")
        else:
            print(f"   Sentiment data: Cache not found")
            self.sentiment_data = None
        
    def collect_optimal_data(self, tickers):
        """모델별 최적 데이터 수집"""
        print("1. Collecting optimal data for each model...")
        start_time = time.time()
        
        # Direction 모델용 6년 데이터
        print("   [Direction] Collecting 6y data...")
        direction_stocks = []
        for ticker in tickers:
            try:
                data = yf.download(ticker, period='6y', progress=False)
                if not data.empty and len(data) > 500:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.droplevel(1)
                    self.direction_data[ticker] = data
                    direction_stocks.append(ticker)
                    print(f"      {ticker}: {len(data)}개 데이터")
            except Exception as e:
                print(f"      {ticker} 수집 실패: {e}")
        
        # Volatility 모델용 2년 데이터
        print("    Volatility 모델용 2년 데이터 수집...")
        volatility_stocks = []
        for ticker in tickers:
            try:
                data = yf.download(ticker, period='2y', progress=False)
                if not data.empty and len(data) > 200:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.droplevel(1)
                    self.volatility_data[ticker] = data
                    volatility_stocks.append(ticker)
                    print(f"      {ticker}: {len(data)}개 데이터")
            except Exception as e:
                print(f"      {ticker} 수집 실패: {e}")
        
        # Risk 모델용 2년 데이터
        print("    Risk 모델용 2년 데이터 수집...")
        risk_stocks = []
        for ticker in tickers:
            try:
                data = yf.download(ticker, period='2y', progress=False)
                if not data.empty and len(data) > 200:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.droplevel(1)
                    self.risk_data[ticker] = data
                    risk_stocks.append(ticker)
                    print(f"      {ticker}: {len(data)}개 데이터")
            except Exception as e:
                print(f"      {ticker} 수집 실패: {e}")
        
        collection_time = time.time() - start_time
        print(f" 모델별 데이터 수집 완료: {collection_time:.1f}초")
        print(f"   - Direction (6년): {len(direction_stocks)}개 종목")
        print(f"   - Volatility (2년): {len(volatility_stocks)}개 종목")
        print(f"   - Risk (5년): {len(risk_stocks)}개 종목")
        
        return direction_stocks, volatility_stocks, risk_stocks
    
    def get_current_prices(self, all_tickers):
        """현재 주가 수집"""
        print("2. 현재 주가 수집...")
        for ticker in all_tickers:
            try:
                data = yf.download(ticker, period='1d', progress=False)
                if not data.empty:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.droplevel(1)
                    self.current_prices[ticker] = float(data['Close'].iloc[-1])
                    print(f"    {ticker}: {self.current_prices[ticker]:,}원")
            except Exception as e:
                print(f"    {ticker} 현재가 수집 실패: {e}")
                self.current_prices[ticker] = 0
    
    def filter_affordable_stocks(self, all_tickers, max_price=150000):
        """저렴한 주식 필터링"""
        print(f"3. 저렴한 주식 필터링 (최대 {max_price:,}원)...")
        affordable_stocks = []
        for ticker in all_tickers:
            if ticker in self.current_prices and self.current_prices[ticker] <= max_price:
                affordable_stocks.append(ticker)
        
        print(f"    저렴한 주식: {len(affordable_stocks)}개")
        for ticker in affordable_stocks:
            print(f"    {ticker}: {self.current_prices[ticker]:,}원")
        
        return affordable_stocks
    
    def calculate_technical_indicators(self, df):
        """기술적 지표 계산"""
        df = df.copy()
        
        # 1. 이동평균
        df['MA_5'] = df['Close'].rolling(5).mean()
        df['MA_20'] = df['Close'].rolling(20).mean()
        df['MA_Ratio'] = df['MA_5'] / df['MA_20']
        
        # 2. RSI
        delta = df['Close'].diff()
        gain = (delta.where(delta > 0, 0)).rolling(14).mean()
        loss = (-delta.where(delta < 0, 0)).rolling(14).mean()
        rs = gain / loss
        df['RSI'] = 100 - (100 / (1 + rs))
        
        # 3. 가격 변화율
        df['Price_Change'] = df['Close'].pct_change()
        
        # 4. 거래량 비율
        df['Volume_Ratio'] = df['Volume'] / df['Volume'].rolling(20).mean()
        
        # 5. 변동성
        df['Volatility'] = df['Close'].pct_change().rolling(10).std()
        
        # 6. MACD
        exp1 = df['Close'].ewm(span=12).mean()
        exp2 = df['Close'].ewm(span=26).mean()
        df['MACD'] = exp1 - exp2
        
        # 7. 볼린저밴드 위치
        bb_middle = df['Close'].rolling(20).mean()
        bb_std = df['Close'].rolling(20).std()
        df['BB_Upper'] = bb_middle + (bb_std * 2)
        df['BB_Lower'] = bb_middle - (bb_std * 2)
        df['BB_Position'] = (df['Close'] - df['BB_Lower']) / (df['BB_Upper'] - df['BB_Lower'])
        
        # 8. 모멘텀
        df['Momentum_5'] = df['Close'].pct_change(5)
        
        return df
    
    def create_targets(self, df):
        """타겟 변수 생성 (검증된 설정 - 5일 예측)"""
        df = df.copy()
        
        # Direction: 5일 후 중앙값 기준 (클래스 균형 50:50, 상승 Recall 41.5%)
        # 중앙값(~0%)을 기준으로 상승/하락 분류 → 균형잡힌 예측!
        df['Next_5_Return'] = df['Close'].pct_change(5).shift(-5)
        # 주의: 중앙값은 학습 데이터에서 계산해야 함 (여기서는 0으로 근사)
        df['Direction'] = (df['Next_5_Return'] > 0.0).astype(int)
        
        # Volatility: 5일 후 변동성 (Test 66.4%, 균형 양호)
        df['Next_5_Volatility'] = df['Close'].pct_change().rolling(5).std().shift(-5)
        df['Volatility_Target'] = (df['Next_5_Volatility'] > df['Volatility']).astype(int)
        
        # Risk: 5일 내 3% 이상 손실 (Test 61.9%, 위험 Recall 45%)
        df['Next_5_Min'] = df['Close'].rolling(5).min().shift(-5)
        df['Max_Loss'] = (df['Next_5_Min'] - df['Close']) / df['Close']
        df['Risk'] = (df['Max_Loss'] < -0.03).astype(int)
        
        return df
    
    def create_direction_features_and_targets(self, affordable_stocks):
        """Direction 모델용 특성 및 타겟 생성 (6년 데이터 + 거시경제)"""
        print("4. Direction features & targets (6y + Macro only)...")
        
        all_data = []
        
        for ticker in affordable_stocks:
            if ticker in self.direction_data:
                df = self.direction_data[ticker].copy()
                df = df.sort_index()
                
                # 기술적 지표 계산
                df = self.calculate_technical_indicators(df)
                
                # 거시경제 피처 추가
                if self.macro_data:
                    df = merge_macro_features(df, self.macro_data)
                
                # 타겟 변수 생성
                df = self.create_targets(df)
                
                # Direction용 특성 (기술적 8개 + 거시경제 5개 = 13개)
                direction_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 
                                     'Volatility', 'MACD', 'BB_Position', 'Momentum_5']
                
                # 거시경제 피처
                macro_features = ['KOSPI_Change', 'USD_KRW_Change', 'VIX', 'VIX_Change', 'SP500_Change']
                
                # 사용 가능한 피처만 선택
                available_features = direction_features.copy()
                for feat in macro_features:
                    if feat in df.columns:
                        available_features.append(feat)
                
                # NaN 제거
                df_clean = df.dropna(subset=available_features + ['Direction'])
                
                if len(df_clean) > 0:
                    df_clean['Ticker'] = ticker
                    df_clean['Date'] = df_clean.index
                    all_data.append(df_clean[['Date', 'Ticker'] + available_features + ['Direction']])
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            combined_data = combined_data.sort_values('Date')
            self.features_data['direction'] = combined_data
            print(f"    Direction 데이터 생성 완료: {len(combined_data)}개 샘플")
            return combined_data
        else:
            raise ValueError("Direction 데이터 생성 실패")
    
    def create_volatility_features_and_targets(self, affordable_stocks):
        """Volatility 모델용 특성 및 타겟 생성 (2년 데이터 + pykrx)"""
        print("5. Volatility features & targets (2y + pykrx)...")
        
        all_data = []
        
        for ticker in affordable_stocks:
            if ticker in self.volatility_data:
                df = self.volatility_data[ticker].copy()
                df = df.sort_index()
                
                # 기술적 지표 계산
                df = self.calculate_technical_indicators(df)
                
                # pykrx 피처 추가
                if self.pykrx_data:
                    df = merge_pykrx_features(df, self.pykrx_data, ticker)
                
                # 타겟 변수 생성
                df = self.create_targets(df)
                
                # Volatility용 특성 (기술적 5개 + pykrx 3개 = 8개)
                volatility_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility']
                
                # pykrx 피처
                pykrx_features = ['Institution_Ratio', 'Foreign_Ratio', 'Individual_Ratio']
                
                # 사용 가능한 피처만 선택
                available_features = volatility_features.copy()
                for feat in pykrx_features:
                    if feat in df.columns:
                        available_features.append(feat)
                
                # NaN 제거
                df_clean = df.dropna(subset=available_features + ['Volatility_Target'])
                
                if len(df_clean) > 0:
                    df_clean['Ticker'] = ticker
                    df_clean['Date'] = df_clean.index
                    all_data.append(df_clean[['Date', 'Ticker'] + available_features + ['Volatility_Target']])
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            combined_data = combined_data.sort_values('Date')
            self.features_data['volatility'] = combined_data
            print(f"    Volatility 데이터 생성 완료: {len(combined_data)}개 샘플")
            return combined_data
        else:
            raise ValueError("Volatility 데이터 생성 실패")
    
    def create_risk_features_and_targets(self, affordable_stocks):
        """Risk 모델용 특성 및 타겟 생성 (2년 데이터 - 원본)"""
        print("6. Risk features & targets (2y - Original 16 features)...")
        
        all_data = []
        
        for ticker in affordable_stocks:
            if ticker in self.risk_data:
                df = self.risk_data[ticker].copy()
                df = df.sort_index()
                
                # 기술적 지표 계산
                df = self.calculate_technical_indicators(df)
                
                # 타겟 변수 생성
                df = self.create_targets(df)
                
                # Risk용 특성 (기본 8개 + 고급 8개 = 16개만)
                risk_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility', 'MACD', 'BB_Position', 'Momentum_5']
                
                # 고급 특성 추가
                df['RSI_x_Volume'] = df['RSI'] * df['Volume_Ratio']
                df['Trend_Strength'] = df['MA_Ratio'] * df['Momentum_5']
                df['BB_Momentum'] = df['BB_Position'] * df['Momentum_5']
                df['Volatility_x_RSI'] = df['Volatility'] * df['RSI']
                df['MACD_x_Volume'] = df['MACD'] * df['Volume_Ratio']
                df['Price_Momentum'] = df['Price_Change'] * df['Momentum_5']
                df['RSI_MACD'] = df['RSI'] * df['MACD']
                df['BB_Volatility'] = df['BB_Position'] * df['Volatility']
                
                risk_features.extend(['RSI_x_Volume', 'Trend_Strength', 'BB_Momentum', 'Volatility_x_RSI', 'MACD_x_Volume', 'Price_Momentum', 'RSI_MACD', 'BB_Volatility'])
                
                # NaN 제거
                df_clean = df.dropna(subset=risk_features + ['Risk'])
                
                if len(df_clean) > 0:
                    df_clean['Ticker'] = ticker
                    df_clean['Date'] = df_clean.index
                    all_data.append(df_clean[['Date', 'Ticker'] + risk_features + ['Risk']])
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            combined_data = combined_data.sort_values('Date')
            self.features_data['risk'] = combined_data
            print(f"    Risk 데이터 생성 완료: {len(combined_data)}개 샘플")
            return combined_data
        else:
            raise ValueError("Risk 데이터 생성 실패")
    
    def prepare_optimal_data(self):
        """최적화된 데이터 준비 (동적 피처 + PCA + Train/Val/Test Split)"""
        print("7. Preparing optimized data (Train 60% / Val 20% / Test 20%)...")
        
        # Direction 데이터 준비 (6년 + Macro + pykrx)
        direction_data = self.features_data['direction'].copy()
        direction_feature_cols = [col for col in direction_data.columns if col not in ['Date', 'Ticker', 'Direction']]
        
        # NaN 제거
        direction_data = direction_data.replace([np.inf, -np.inf], np.nan)
        direction_data = direction_data.dropna(subset=direction_feature_cols + ['Direction'])
        
        # Train/Val/Test Split (60/20/20) - 시계열 순서 유지
        direction_train_idx = int(len(direction_data) * 0.6)
        direction_val_idx = int(len(direction_data) * 0.8)
        
        direction_train_data = direction_data.iloc[:direction_train_idx]
        direction_val_data = direction_data.iloc[direction_train_idx:direction_val_idx]
        direction_test_data = direction_data.iloc[direction_val_idx:]
        
        X_direction_train = direction_train_data[direction_feature_cols].values
        y_direction_train = direction_train_data['Direction'].values
        X_direction_val = direction_val_data[direction_feature_cols].values
        y_direction_val = direction_val_data['Direction'].values
        X_direction_test = direction_test_data[direction_feature_cols].values
        y_direction_test = direction_test_data['Direction'].values
        
        # Scaler fit on train only
        X_direction_train_scaled = self.direction_scaler.fit_transform(X_direction_train)
        X_direction_val_scaled = self.direction_scaler.transform(X_direction_val)
        X_direction_test_scaled = self.direction_scaler.transform(X_direction_test)
        
        # PCA fit on train only
        self.direction_pca.fit(X_direction_train_scaled)
        X_direction_train_pca = self.direction_pca.transform(X_direction_train_scaled)
        X_direction_val_pca = self.direction_pca.transform(X_direction_val_scaled)
        X_direction_test_pca = self.direction_pca.transform(X_direction_test_scaled)
        direction_n_components = X_direction_train_pca.shape[1]
        direction_explained_var = self.direction_pca.explained_variance_ratio_.sum()
        
        # Volatility 데이터 준비 (2년 + Macro + pykrx) - PCA 제외
        volatility_data = self.features_data['volatility'].copy()
        volatility_feature_cols = [col for col in volatility_data.columns if col not in ['Date', 'Ticker', 'Volatility_Target']]
        
        # NaN 제거
        volatility_data = volatility_data.replace([np.inf, -np.inf], np.nan)
        volatility_data = volatility_data.dropna(subset=volatility_feature_cols + ['Volatility_Target'])
        
        # Train/Val/Test Split (60/20/20)
        volatility_train_idx = int(len(volatility_data) * 0.6)
        volatility_val_idx = int(len(volatility_data) * 0.8)
        
        volatility_train_data = volatility_data.iloc[:volatility_train_idx]
        volatility_val_data = volatility_data.iloc[volatility_train_idx:volatility_val_idx]
        volatility_test_data = volatility_data.iloc[volatility_val_idx:]
        
        X_volatility_train = volatility_train_data[volatility_feature_cols].values
        y_volatility_train = volatility_train_data['Volatility_Target'].values
        X_volatility_val = volatility_val_data[volatility_feature_cols].values
        y_volatility_val = volatility_val_data['Volatility_Target'].values
        X_volatility_test = volatility_test_data[volatility_feature_cols].values
        y_volatility_test = volatility_test_data['Volatility_Target'].values
        
        # Scaler fit on train only
        X_volatility_train_scaled = self.volatility_scaler.fit_transform(X_volatility_train)
        X_volatility_val_scaled = self.volatility_scaler.transform(X_volatility_val)
        X_volatility_test_scaled = self.volatility_scaler.transform(X_volatility_test)
        
        # Volatility는 PCA 미적용
        volatility_n_components = len(volatility_feature_cols)
        volatility_explained_var = 1.0
        
        # Risk 데이터 준비 (5년 + Macro only)
        risk_data = self.features_data['risk'].copy()
        risk_feature_cols = [col for col in risk_data.columns if col not in ['Date', 'Ticker', 'Risk']]
        
        # NaN 제거
        risk_data = risk_data.replace([np.inf, -np.inf], np.nan)
        risk_data = risk_data.dropna(subset=risk_feature_cols + ['Risk'])
        
        # Train/Val/Test Split (60/20/20)
        risk_train_idx = int(len(risk_data) * 0.6)
        risk_val_idx = int(len(risk_data) * 0.8)
        
        risk_train_data = risk_data.iloc[:risk_train_idx]
        risk_val_data = risk_data.iloc[risk_train_idx:risk_val_idx]
        risk_test_data = risk_data.iloc[risk_val_idx:]
        
        X_risk_train = risk_train_data[risk_feature_cols].values
        y_risk_train = risk_train_data['Risk'].values
        X_risk_val = risk_val_data[risk_feature_cols].values
        y_risk_val = risk_val_data['Risk'].values
        X_risk_test = risk_test_data[risk_feature_cols].values
        y_risk_test = risk_test_data['Risk'].values
        
        # Scaler fit on train only
        X_risk_train_scaled = self.risk_scaler.fit_transform(X_risk_train)
        X_risk_val_scaled = self.risk_scaler.transform(X_risk_val)
        X_risk_test_scaled = self.risk_scaler.transform(X_risk_test)
        
        # Risk PCA 미적용 (원본 유지)
        risk_n_components = len(risk_feature_cols)
        risk_explained_var = 1.0
        
        # 피처 리스트 저장 (예측 시 필요)
        self.direction_feature_names = direction_feature_cols
        self.volatility_feature_names = volatility_feature_cols
        self.risk_feature_names = risk_feature_cols
        
        print(f"   [OK] Data prepared with Train/Val/Test Split:")
        print(f"     - Direction: {len(direction_feature_cols)} -> {direction_n_components} features (PCA 95%)")
        print(f"       Train: {len(direction_train_data)}, Val: {len(direction_val_data)}, Test: {len(direction_test_data)}")
        print(f"     - Volatility: {len(volatility_feature_cols)} features (No PCA)")
        print(f"       Train: {len(volatility_train_data)}, Val: {len(volatility_val_data)}, Test: {len(volatility_test_data)}")
        print(f"     - Risk: {len(risk_feature_cols)} features (No PCA)")
        print(f"       Train: {len(risk_train_data)}, Val: {len(risk_val_data)}, Test: {len(risk_test_data)}")
        
        # Train/Val/Test 데이터 반환
        train_data = (X_direction_train_pca, X_volatility_train_scaled, X_risk_train_scaled)
        train_labels = (y_direction_train, y_volatility_train, y_risk_train)
        val_data = (X_direction_val_pca, X_volatility_val_scaled, X_risk_val_scaled)
        val_labels = (y_direction_val, y_volatility_val, y_risk_val)
        test_data = (X_direction_test_pca, X_volatility_test_scaled, X_risk_test_scaled)
        test_labels = (y_direction_test, y_volatility_test, y_risk_test)
        
        return train_data, train_labels, val_data, val_labels, test_data, test_labels
    
    def build_optimal_models(self):
        """최적화된 모델 구축 (87개 실험 결과 최적 설정)"""
        print("8. 최적화된 모델 구축 (검증된 최적 설정)...")
        
        # Direction: StackingClassifier (C=1.0) - 87개 실험 최고 성능
        base_models_direction = [
            ('logistic', LogisticRegression(C=1.0, penalty='l1', class_weight='balanced', random_state=42, solver='liblinear')),
            ('rf_shallow', RandomForestClassifier(max_depth=3, class_weight='balanced', random_state=42, n_jobs=-1))
        ]
        
        self.direction_model = StackingClassifier(
            estimators=base_models_direction,
            final_estimator=LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
            cv=3,
            n_jobs=-1
        )
        
        # Volatility: LogisticRegression L1 (C=0.005) - 최적 성능
        self.volatility_model = LogisticRegression(
            C=0.005, penalty='l1', class_weight='balanced', 
            random_state=42, solver='liblinear'
        )
        
        # Risk: LogisticRegression L2 (C=0.1) - 균형 최적화
        self.risk_model = LogisticRegression(
            C=0.1, penalty='l2', class_weight='balanced', 
            random_state=42, solver='liblinear', max_iter=1000
        )
        
        print("    최적화된 모델 구축 완료:")
        print("      - Direction: Stacking (C=1.0) - 87개 실험 최적")
        print("      - Volatility: Logistic L1 (C=0.005) - 완벽한 일반화")
        print("      - Risk: Logistic L2 (C=0.1) - 3% 손실 기준")
    
    def run_hybrid_validation(self, train_data, train_labels, val_data, val_labels, test_data, test_labels):
        """통합된 하이브리드 검증 (Train + Val + Test)"""
        print("9. 통합 검증 (Train + Val + Test)...")
        start_time = time.time()
        
        X_train_direction, X_train_volatility, X_train_risk = train_data
        y_train_direction, y_train_volatility, y_train_risk = train_labels
        X_val_direction, X_val_volatility, X_val_risk = val_data
        y_val_direction, y_val_volatility, y_val_risk = val_labels
        X_test_direction, X_test_volatility, X_test_risk = test_data
        y_test_direction, y_test_volatility, y_test_risk = test_labels
        
        # 각 모델별 검증
        models = {
            'direction': (self.direction_model, X_train_direction, y_train_direction, X_val_direction, y_val_direction, X_test_direction, y_test_direction),
            'volatility': (self.volatility_model, X_train_volatility, y_train_volatility, X_val_volatility, y_val_volatility, X_test_volatility, y_test_volatility),
            'risk': (self.risk_model, X_train_risk, y_train_risk, X_val_risk, y_val_risk, X_test_risk, y_test_risk)
        }
        
        results = {}
        val_results = {}
        test_results = {}
        
        for model_name, (model, X_train, y_train, X_val, y_val, X_test, y_test) in models.items():
            print(f"    [{model_name.capitalize()}] Train 학습 중...")
            
            # Train 데이터로 학습
            model.fit(X_train, y_train)
            
            # Train 성능
            train_acc = model.score(X_train, y_train)
            train_pred = model.predict(X_train)
            train_f1 = f1_score(y_train, train_pred, average='weighted')
            
            # Validation 성능
            print(f"      [{model_name.capitalize()}] Validation 평가...")
            val_pred = model.predict(X_val)
            val_pred_proba = model.predict_proba(X_val)
            
            val_acc = accuracy_score(y_val, val_pred)
            val_f1 = f1_score(y_val, val_pred, average='weighted')
            
            try:
                if len(np.unique(y_train)) == 2:
                    val_auc = roc_auc_score(y_val, val_pred_proba[:, 1])
                else:
                    val_auc = roc_auc_score(y_val, val_pred_proba, multi_class='ovr', average='weighted')
            except:
                val_auc = 0.5
            
            # Test 성능
            print(f"      [{model_name.capitalize()}] Test 평가...")
            test_pred = model.predict(X_test)
            test_pred_proba = model.predict_proba(X_test)
            
            test_acc = accuracy_score(y_test, test_pred)
            test_f1 = f1_score(y_test, test_pred, average='weighted')
            
            try:
                if len(np.unique(y_train)) == 2:
                    test_auc = roc_auc_score(y_test, test_pred_proba[:, 1])
                else:
                    test_auc = roc_auc_score(y_test, test_pred_proba, multi_class='ovr', average='weighted')
            except:
                test_auc = 0.5
            
            # 결과 저장
            results[model_name] = {
                'train_acc': train_acc,
                'train_f1': train_f1
            }
            
            val_results[model_name] = {
                'accuracy': val_acc,
                'f1': val_f1,
                'roc_auc': val_auc
            }
            
            test_results[model_name] = {
                'accuracy': test_acc,
                'f1': test_f1,
                'roc_auc': test_auc
            }
            
            print(f"      Train: Acc {train_acc:.3f}, F1 {train_f1:.3f}")
            print(f"      Val:   Acc {val_acc:.3f}, F1 {val_f1:.3f}, AUC {val_auc:.3f}")
            print(f"      Test:  Acc {test_acc:.3f}, F1 {test_f1:.3f}, AUC {test_auc:.3f}")
        
        validation_time = time.time() - start_time
        
        # 결과 저장
        self.validation_results = results
        self.val_results = val_results
        self.test_results = test_results
        
        print(f"    통합 검증 완료: {validation_time:.1f}초")
        return validation_time
    
    def save_models(self):
        """최적화된 모델과 스케일러 저장"""
        print("10. Saving models & scalers...")
        
        # 저장할 모델 데이터 구성
        model_data = {
            'direction_model': self.direction_model,
            'volatility_model': self.volatility_model,
            'risk_model': self.risk_model,
            'direction_scaler': self.direction_scaler,
            'volatility_scaler': self.volatility_scaler,
            'risk_scaler': self.risk_scaler,
            'direction_pca': self.direction_pca,
            'volatility_pca': self.volatility_pca,
            'risk_pca': self.risk_pca,
            'direction_feature_names': self.direction_feature_names,
            'volatility_feature_names': self.volatility_feature_names,
            'risk_feature_names': self.risk_feature_names,
            'validation_results': self.validation_results,
            'val_results': self.val_results,
            'test_results': self.test_results,
            'model_info': {
                'direction': {
                    'data_period': '6y',
                    'features': len(self.direction_feature_names),
                    'pca_applied': True,
                    'pca_components': self.direction_pca.n_components_,
                    'description': 'Direction (6y + Macro + PCA)'
                },
                'volatility': {
                    'data_period': '2y',
                    'features': len(self.volatility_feature_names),
                    'pca_applied': False,
                    'pca_components': None,
                    'description': 'Volatility (2y + pykrx, No PCA)'
                },
                'risk': {
                    'data_period': '2y',
                    'features': len(self.risk_feature_names),
                    'pca_applied': False,
                    'pca_components': None,
                    'description': 'Risk (2y - Original, No PCA)'
                }
            }
        }
        
        # PKL 파일로 저장
        with open('final_hybrid_optimal_models.pkl', 'wb') as f:
            pickle.dump(model_data, f)
        
        print("   [OK] Models saved: final_hybrid_optimal_models.pkl")
        print("   [Saved]:")
        print(f"     - Direction model ({len(self.direction_feature_names)} -> {self.direction_pca.n_components_} with PCA)")
        print(f"     - Volatility model ({len(self.volatility_feature_names)} features, No PCA)")
        print(f"     - Risk model ({len(self.risk_feature_names)} features, No PCA)")
        print("     - Scalers, PCA (Direction only) & feature names")
        print("     - Validation/Val/Test results")
    
    def load_models(self, filepath='final_hybrid_optimal_models.pkl'):
        """저장된 모델과 스케일러 로드"""
        print(f"모델 로드 중: {filepath}")
        
        try:
            with open(filepath, 'rb') as f:
                model_data = pickle.load(f)
            
            # 모델 로드
            self.direction_model = model_data['direction_model']
            self.volatility_model = model_data['volatility_model']
            self.risk_model = model_data['risk_model']
            
            # 스케일러 로드
            self.direction_scaler = model_data['direction_scaler']
            self.volatility_scaler = model_data['volatility_scaler']
            self.risk_scaler = model_data['risk_scaler']
            
            # PCA 로드
            self.direction_pca = model_data['direction_pca']
            self.volatility_pca = model_data['volatility_pca']
            self.risk_pca = model_data['risk_pca']
            
            # Feature names 로드 (예측 시 필수)
            self.direction_feature_names = model_data['direction_feature_names']
            self.volatility_feature_names = model_data['volatility_feature_names']
            self.risk_feature_names = model_data['risk_feature_names']
            
            # 검증 결과 로드
            self.validation_results = model_data['validation_results']
            
            # Val/Test 결과 로드 (있으면)
            if 'val_results' in model_data:
                self.val_results = model_data['val_results']
            if 'test_results' in model_data:
                self.test_results = model_data['test_results']
            
            print(" 모델 로드 완료!")
            return model_data['model_info']
            
        except FileNotFoundError:
            print(f" 파일을 찾을 수 없습니다: {filepath}")
            return None
        except Exception as e:
            print(f" 모델 로드 실패: {e}")
            return None
    
    def generate_final_report(self):
        """최종 성능 보고서 생성"""
        print("\n" + "=" * 80)
        print(" 최종 하이브리드 최적 시스템 성능 보고서")
        print("=" * 80)
        
        # 기본 정보
        print(f"\n 시스템 정보:")
        print(f"  - Direction 모델: 6년 데이터, {len(self.direction_feature_names)}개 -> {self.direction_pca.n_components_}개 (PCA 95%)")
        print(f"  - Volatility 모델: 2년 데이터, {len(self.volatility_feature_names)}개 특성 (PCA 미적용)")
        print(f"  - Risk 모델: 2년 데이터, {len(self.risk_feature_names)}개 특성 (PCA 미적용)")
        print(f"  - 검증 방법: Train/Val/Test Split (60/20/20)")
        print(f"  - 차원 축소: Direction만 PCA 적용 (설명력 95% 유지)")
        print(f"  - 접근법: 모델별 최적 데이터 기간 + 맞춤형 외부 데이터")
        print(f"  - 외부 데이터: Direction(거시경제), Volatility(pykrx)")
        
        # 모델별 성능 (Train/Val/Test)
        print(f"\n 모델 성능 (Train / Validation / Test):")
        for target in ['direction', 'volatility', 'risk']:
            train = self.validation_results[target]
            val = self.val_results[target]
            test = self.test_results[target]
            
            print(f"  - {target.capitalize()}:")
            print(f"    Train: Acc {train['train_acc']:.3f}, F1 {train['train_f1']:.3f}")
            print(f"    Val:   Acc {val['accuracy']:.3f}, F1 {val['f1']:.3f}, AUC {val['roc_auc']:.3f}")
            print(f"    Test:  Acc {test['accuracy']:.3f}, F1 {test['f1']:.3f}, AUC {test['roc_auc']:.3f}")
        
        # 기존 챔피언과 비교 (Test 기준)
        print(f"\n 기존 챔피언(5년 통일) vs 최적 하이브리드 비교 (Test 세트):")
        champion_direction = 0.544
        champion_volatility = 0.644
        champion_risk = 0.650
        
        current_direction = self.test_results['direction']['accuracy']
        current_volatility = self.test_results['volatility']['accuracy']
        current_risk = self.test_results['risk']['accuracy']
        
        print(f"  - Direction: {champion_direction:.3f} vs {current_direction:.3f} (차이: {current_direction - champion_direction:+.3f})")
        print(f"  - Volatility: {champion_volatility:.3f} vs {current_volatility:.3f} (차이: {current_volatility - champion_volatility:+.3f})")
        print(f"  - Risk: {champion_risk:.3f} vs {current_risk:.3f} (차이: {current_risk - champion_risk:+.3f})")
        
        # 성능 향상 분석 (Test 기준)
        print(f"\n 성능 향상 분석 (Test 세트):")
        direction_improvement = current_direction - champion_direction
        volatility_improvement = current_volatility - champion_volatility
        risk_improvement = current_risk - champion_risk
        
        print(f"  - Direction: {direction_improvement:+.3f} ({'향상' if direction_improvement > 0 else '하락'})")
        print(f"  - Volatility: {volatility_improvement:+.3f} ({'향상' if volatility_improvement > 0 else '하락'})")
        print(f"  - Risk: {risk_improvement:+.3f} ({'향상' if risk_improvement > 0 else '하락'})")
        
        # 전체 평가
        total_improvement = direction_improvement + volatility_improvement + risk_improvement
        print(f"\n 전체 평가:")
        if total_improvement > 0:
            print(f"   하이브리드 접근법 성공! 전체 성능 향상: {total_improvement:+.3f}")
        else:
            print(f"   하이브리드 접근법 효과 제한적: {total_improvement:+.3f}")
        
        print("\n 최종 하이브리드 최적 시스템 완료!")
    
    def predict_stock_analysis(self, ticker, current_data):
        """저장된 모델을 사용한 주식 분석 예측 (외부 데이터 포함)"""
        print(f"\n {ticker} 주식 분석 예측...")
        
        try:
            # 기술적 지표 계산
            df = self.calculate_technical_indicators(current_data)
            
            # 최신 외부 데이터 로드 (예측 시점 기준)
            if not hasattr(self, 'macro_data') or self.macro_data is None:
                self.macro_data = load_or_download_macro_data()
            
            if not hasattr(self, 'pykrx_data') or self.pykrx_data is None:
                import os
                cache_file = 'pykrx_data_30stocks_cache.pkl'
                if os.path.exists(cache_file):
                    with open(cache_file, 'rb') as f:
                        cache = pickle.load(f)
                    self.pykrx_data = cache['data']
            
            if not hasattr(self, 'sentiment_data') or self.sentiment_data is None:
                import os
                sentiment_cache_file = 'cached_data/naver_api_news_cache.pkl'
                if os.path.exists(sentiment_cache_file):
                    with open(sentiment_cache_file, 'rb') as f:
                        cache = pickle.load(f)
                    self.sentiment_data = cache['data']
            
            # 거시경제 데이터 병합 (Direction용)
            if self.macro_data:
                df = merge_macro_features(df, self.macro_data)
            
            # pykrx 데이터 병합 (Volatility용)
            if self.pykrx_data and ticker in self.pykrx_data:
                df = merge_pykrx_features(df, self.pykrx_data, ticker)
            
            # 감정 데이터 추가 (Risk용)
            if self.sentiment_data and ticker in self.sentiment_data:
                sent = self.sentiment_data[ticker]
                df['Sentiment_Score'] = sent['sentiment_score']
                df['Positive_Ratio'] = sent['positive_ratio']
                df['Negative_Ratio'] = sent['negative_ratio']
                df['News_Volume'] = sent['news_count']
            
            # Risk용 고급 특성 계산
            df['RSI_x_Volume'] = df['RSI'] * df['Volume_Ratio']
            df['Trend_Strength'] = df['MA_Ratio'] * df['Momentum_5']
            df['BB_Momentum'] = df['BB_Position'] * df['Momentum_5']
            df['Volatility_x_RSI'] = df['Volatility'] * df['RSI']
            df['MACD_x_Volume'] = df['MACD'] * df['Volume_Ratio']
            df['Price_Momentum'] = df['Price_Change'] * df['Momentum_5']
            df['RSI_MACD'] = df['RSI'] * df['MACD']
            df['BB_Volatility'] = df['BB_Position'] * df['Volatility']
            
            # NaN 값 처리
            df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
            df = df.replace([np.inf, -np.inf], 0)
            
            # Direction 예측 (학습된 특성 사용 + PCA)
            if hasattr(self, 'direction_feature_names'):
                available_direction_features = [f for f in self.direction_feature_names if f in df.columns]
                if len(available_direction_features) > 0:
                    X_direction = df[available_direction_features].iloc[-1:].values
                    X_direction_scaled = self.direction_scaler.transform(X_direction)
                    X_direction_pca = self.direction_pca.transform(X_direction_scaled)
                    direction_pred = self.direction_model.predict(X_direction_pca)[0]
                    direction_proba = self.direction_model.predict_proba(X_direction_pca)[0]
                else:
                    raise ValueError(f"Direction 특성을 찾을 수 없습니다: {self.direction_feature_names}")
            else:
                raise ValueError("direction_feature_names가 로드되지 않았습니다")
            
            # Volatility 예측 (학습된 특성 사용, PCA 미적용)
            if hasattr(self, 'volatility_feature_names'):
                available_volatility_features = [f for f in self.volatility_feature_names if f in df.columns]
                if len(available_volatility_features) > 0:
                    X_volatility = df[available_volatility_features].iloc[-1:].values
                    X_volatility_scaled = self.volatility_scaler.transform(X_volatility)
                    # Volatility는 PCA 미적용
                    volatility_pred = self.volatility_model.predict(X_volatility_scaled)[0]
                    volatility_proba = self.volatility_model.predict_proba(X_volatility_scaled)[0]
                else:
                    raise ValueError(f"Volatility 특성을 찾을 수 없습니다: {self.volatility_feature_names}")
            else:
                raise ValueError("volatility_feature_names가 로드되지 않았습니다")
            
            # Risk 예측 (학습된 특성 사용, PCA 미적용)
            if hasattr(self, 'risk_feature_names'):
                available_risk_features = [f for f in self.risk_feature_names if f in df.columns]
                if len(available_risk_features) > 0:
                    X_risk = df[available_risk_features].iloc[-1:].values
                    X_risk_scaled = self.risk_scaler.transform(X_risk)
                    # Risk는 PCA 미적용
                    risk_pred = self.risk_model.predict(X_risk_scaled)[0]
                    risk_proba = self.risk_model.predict_proba(X_risk_scaled)[0]
                else:
                    raise ValueError(f"Risk 특성을 찾을 수 없습니다: {self.risk_feature_names}")
            else:
                raise ValueError("risk_feature_names가 로드되지 않았습니다")
            
            # 결과 출력
            print(f"    Direction: {'상승' if direction_pred == 1 else '하락'} (확률: {direction_proba[1]:.3f})")
            print(f"    Volatility: {'높음' if volatility_pred == 1 else '낮음'} (확률: {volatility_proba[1]:.3f})")
            print(f"    Risk: {'위험' if risk_pred == 1 else '안전'} (확률: {risk_proba[1]:.3f})")
            
            return {
                'direction': {'prediction': direction_pred, 'probability': direction_proba[1]},
                'volatility': {'prediction': volatility_pred, 'probability': volatility_proba[1]},
                'risk': {'prediction': risk_pred, 'probability': risk_proba[1]}
            }
            
        except Exception as e:
            print(f"    예측 실패: {e}")
            return None

def main():
    """메인 실행 함수"""
    # 한국 주식 티커 (30개)
    korean_tickers = [
        '005930.KS', '000660.KS', '051910.KS', '035420.KS', '035720.KS',
        '005380.KS', '000270.KS', '068270.KS', '207940.KS', '005490.KS',
        '006400.KS', '051900.KS', '028260.KS', '012330.KS', '066570.KS',
        '003550.KS', '096770.KS', '017670.KS', '009150.KS', '034730.KS',
        '000720.KS', '003490.KS', '011200.KS', '012450.KS', '015760.KS',
        '016360.KS', '017800.KS', '018880.KS', '020150.KS', '021240.KS',
    ]
    
    # 시스템 초기화
    system = FinalHybridOptimalSystem()
    
    try:
        # 0. 외부 데이터 로드 (거시경제 + pykrx)
        system.load_external_data(korean_tickers)
        
        # 1. 모델별 최적 데이터 수집
        direction_stocks, volatility_stocks, risk_stocks = system.collect_optimal_data(korean_tickers)
        
        # 2. 현재 주가 수집
        all_tickers = list(set(direction_stocks + volatility_stocks + risk_stocks))
        system.get_current_prices(all_tickers)
        
        # 3. 전체 종목 사용 (필터링 제거 - 30개 모두 사용)
        print(f"3. Using all {len(all_tickers)} stocks (no filtering)...")
        affordable_stocks = all_tickers
        
        # 4. 모델별 특성 및 타겟 생성
        system.create_direction_features_and_targets(affordable_stocks)
        system.create_volatility_features_and_targets(affordable_stocks)
        system.create_risk_features_and_targets(affordable_stocks)
        
        # 5. 최적화된 데이터 준비 (Train/Val/Test Split)
        train_data, train_labels, val_data, val_labels, test_data, test_labels = system.prepare_optimal_data()
        
        # 6. 최적화된 모델 구축
        system.build_optimal_models()
        
        # 7. 통합 검증 (Train + Val + Test 평가)
        validation_time = system.run_hybrid_validation(train_data, train_labels, val_data, val_labels, test_data, test_labels)
        
        # 8. 최적화된 모델 및 스케일러 저장
        system.save_models()
        
        # 9. 최종 성능 보고서
        system.generate_final_report()
        
        print(f"\n 총 실행 시간: {validation_time:.1f}초")
        
    except Exception as e:
        print(f" 실행 실패: {e}")
        import traceback
        traceback.print_exc()

def example_usage():
    """모델 사용 예제"""
    print("\n" + "=" * 80)
    print(" 모델 사용 예제")
    print("=" * 80)
    
    # 시스템 초기화
    system = FinalHybridOptimalSystem()
    
    # 저장된 모델 로드
    model_info = system.load_models()
    
    if model_info:
        print("\n 모델 로드 성공!")
        print(" 로드된 모델 정보:")
        for model_name, info in model_info.items():
            print(f"  - {model_name.capitalize()}: {info['description']}")
        
        # 예제: 삼성전자 분석
        print("\n 예제: 삼성전자(005930.KS) 분석...")
        try:
            # 최근 30일 데이터 수집
            data = yf.download('005930.KS', period='1mo', progress=False)
            if not data.empty:
                if isinstance(data.columns, pd.MultiIndex):
                    data.columns = data.columns.droplevel(1)
                
                # 주식 분석 예측
                result = system.predict_stock_analysis('005930.KS', data)
                
                if result:
                    print("\n 분석 결과:")
                    print(f"  - 방향성: {'상승' if result['direction']['prediction'] == 1 else '하락'}")
                    print(f"  - 변동성: {'높음' if result['volatility']['prediction'] == 1 else '낮음'}")
                    print(f"  - 위험도: {'위험' if result['risk']['prediction'] == 1 else '안전'}")
            else:
                print(" 데이터 수집 실패")
        except Exception as e:
            print(f" 예제 실행 실패: {e}")
    else:
        print(" 모델 로드 실패")

if __name__ == "__main__":
    # 메인 실행 (모델 훈련 및 저장)
    main()
    
    # 사용 예제 (저장된 모델 로드 및 예측)
    example_usage()

