"""
매주 실행되는 모델 재학습 시스템
- 전체 최신 데이터로 모델 재훈련
- final_hybrid_optimal_models.pkl 업데이트
"""

import numpy as np
import pandas as pd
import yfinance as yf
from sklearn.model_selection import TimeSeriesSplit
from sklearn.preprocessing import RobustScaler
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier, StackingClassifier
from sklearn.metrics import accuracy_score, f1_score, roc_auc_score
import time
import pickle
import warnings
warnings.filterwarnings('ignore')

class WeeklyTrainer:
    def __init__(self):
        self.korean_tickers = [
            '005930.KS', '000660.KS', '051910.KS', '035420.KS', '035720.KS',
            '005380.KS', '000270.KS', '068270.KS', '207940.KS', '005490.KS',
            '006400.KS', '051900.KS', '028260.KS', '012330.KS', '066570.KS',
            '003550.KS', '096770.KS', '017670.KS', '009150.KS', '034730.KS',
            '000720.KS', '003490.KS', '011200.KS', '012450.KS', '015760.KS',
            '016360.KS', '017800.KS', '018880.KS', '020150.KS', '021240.KS',
        ]
        
        # 모델별 데이터 저장소
        self.direction_data = {}
        self.volatility_data = {}
        self.risk_data = {}
        
        # 스케일러
        self.direction_scaler = RobustScaler()
        self.volatility_scaler = RobustScaler()
        self.risk_scaler = RobustScaler()
        
        # 모델들
        self.direction_model = None
        self.volatility_model = None
        self.risk_model = None
        
    def collect_optimal_data(self):
        """모델별 최적 데이터 수집"""
        print("1. 모델별 최적 데이터 수집...")
        start_time = time.time()
        
        # Direction 모델용 6년 데이터
        print("   📊 Direction 모델용 6년 데이터 수집...")
        direction_stocks = []
        for ticker in self.korean_tickers:
            try:
                data = yf.download(ticker, period='6y', progress=False)
                if not data.empty and len(data) > 500:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.droplevel(1)
                    self.direction_data[ticker] = data
                    direction_stocks.append(ticker)
                    print(f"     ✅ {ticker}: {len(data)}개 데이터")
            except Exception as e:
                print(f"     ❌ {ticker} 수집 실패: {e}")
        
        # Volatility 모델용 2년 데이터
        print("   📊 Volatility 모델용 2년 데이터 수집...")
        volatility_stocks = []
        for ticker in self.korean_tickers:
            try:
                data = yf.download(ticker, period='2y', progress=False)
                if not data.empty and len(data) > 200:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.droplevel(1)
                    self.volatility_data[ticker] = data
                    volatility_stocks.append(ticker)
                    print(f"     ✅ {ticker}: {len(data)}개 데이터")
            except Exception as e:
                print(f"     ❌ {ticker} 수집 실패: {e}")
        
        # Risk 모델용 5년 데이터
        print("   📊 Risk 모델용 5년 데이터 수집...")
        risk_stocks = []
        for ticker in self.korean_tickers:
            try:
                data = yf.download(ticker, period='5y', progress=False)
                if not data.empty and len(data) > 400:
                    if isinstance(data.columns, pd.MultiIndex):
                        data.columns = data.columns.droplevel(1)
                    self.risk_data[ticker] = data
                    risk_stocks.append(ticker)
                    print(f"     ✅ {ticker}: {len(data)}개 데이터")
            except Exception as e:
                print(f"     ❌ {ticker} 수집 실패: {e}")
        
        collection_time = time.time() - start_time
        print(f"✅ 모델별 데이터 수집 완료: {collection_time:.1f}초")
        print(f"   - Direction (6년): {len(direction_stocks)}개 종목")
        print(f"   - Volatility (2년): {len(volatility_stocks)}개 종목")
        print(f"   - Risk (5년): {len(risk_stocks)}개 종목")
        
        return direction_stocks, volatility_stocks, risk_stocks
    
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
        """타겟 변수 생성"""
        df = df.copy()
        
        # Direction: 2지선다 (상승/하락)
        df['Next_5_Return'] = df['Close'].pct_change(5).shift(-5)
        df['Direction'] = (df['Next_5_Return'] > 0.01).astype(int)
        
        # Volatility: 5일 후 변동성 비교
        df['Next_5_Volatility'] = df['Close'].pct_change().rolling(5).std().shift(-5)
        df['Volatility_Target'] = (df['Next_5_Volatility'] > df['Volatility']).astype(int)
        
        # Risk: 2지선다 (안전/위험)
        df['Next_5_Min'] = df['Close'].rolling(5).min().shift(-5)
        df['Max_Loss'] = (df['Next_5_Min'] - df['Close']) / df['Close']
        df['Risk'] = (df['Max_Loss'] < -0.05).astype(int)
        
        return df
    
    def create_direction_features_and_targets(self, affordable_stocks):
        """Direction 모델용 특성 및 타겟 생성 (6년 데이터)"""
        print("2. Direction 모델용 특성 및 타겟 생성 (6년 데이터)...")
        
        all_data = []
        
        for ticker in affordable_stocks:
            if ticker in self.direction_data:
                df = self.direction_data[ticker].copy()
                df = df.sort_index()
                
                # 기술적 지표 계산
                df = self.calculate_technical_indicators(df)
                
                # 타겟 변수 생성
                df = self.create_targets(df)
                
                # Direction용 8개 특성
                direction_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility', 'MACD', 'BB_Position', 'Momentum_5']
                
                # NaN 제거
                df_clean = df.dropna(subset=direction_features + ['Direction'])
                
                if len(df_clean) > 0:
                    df_clean['Ticker'] = ticker
                    df_clean['Date'] = df_clean.index
                    all_data.append(df_clean[['Date', 'Ticker'] + direction_features + ['Direction']])
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            combined_data = combined_data.sort_values('Date')
            print(f"   ✅ Direction 데이터 생성 완료: {len(combined_data)}개 샘플")
            return combined_data
        else:
            raise ValueError("Direction 데이터 생성 실패")
    
    def create_volatility_features_and_targets(self, affordable_stocks):
        """Volatility 모델용 특성 및 타겟 생성 (2년 데이터)"""
        print("3. Volatility 모델용 특성 및 타겟 생성 (2년 데이터)...")
        
        all_data = []
        
        for ticker in affordable_stocks:
            if ticker in self.volatility_data:
                df = self.volatility_data[ticker].copy()
                df = df.sort_index()
                
                # 기술적 지표 계산
                df = self.calculate_technical_indicators(df)
                
                # 타겟 변수 생성
                df = self.create_targets(df)
                
                # Volatility용 5개 특성
                volatility_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility']
                
                # NaN 제거
                df_clean = df.dropna(subset=volatility_features + ['Volatility_Target'])
                
                if len(df_clean) > 0:
                    df_clean['Ticker'] = ticker
                    df_clean['Date'] = df_clean.index
                    all_data.append(df_clean[['Date', 'Ticker'] + volatility_features + ['Volatility_Target']])
        
        if all_data:
            combined_data = pd.concat(all_data, ignore_index=True)
            combined_data = combined_data.sort_values('Date')
            print(f"   ✅ Volatility 데이터 생성 완료: {len(combined_data)}개 샘플")
            return combined_data
        else:
            raise ValueError("Volatility 데이터 생성 실패")
    
    def create_risk_features_and_targets(self, affordable_stocks):
        """Risk 모델용 특성 및 타겟 생성 (5년 데이터)"""
        print("4. Risk 모델용 특성 및 타겟 생성 (5년 데이터)...")
        
        all_data = []
        
        for ticker in affordable_stocks:
            if ticker in self.risk_data:
                df = self.risk_data[ticker].copy()
                df = df.sort_index()
                
                # 기술적 지표 계산
                df = self.calculate_technical_indicators(df)
                
                # 타겟 변수 생성
                df = self.create_targets(df)
                
                # Risk용 16개 특성 (기본 8개 + 고급 8개)
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
            print(f"   ✅ Risk 데이터 생성 완료: {len(combined_data)}개 샘플")
            return combined_data
        else:
            raise ValueError("Risk 데이터 생성 실패")
    
    def prepare_data(self, direction_data, volatility_data, risk_data):
        """데이터 준비"""
        print("5. 데이터 준비...")
        
        # Direction 데이터 준비 (6년, 8개 특성)
        direction_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility', 'MACD', 'BB_Position', 'Momentum_5']
        X_direction = direction_data[direction_features].values
        y_direction = direction_data['Direction'].values
        X_direction_scaled = self.direction_scaler.fit_transform(X_direction)
        
        # Volatility 데이터 준비 (2년, 5개 특성)
        volatility_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility']
        X_volatility = volatility_data[volatility_features].values
        y_volatility = volatility_data['Volatility_Target'].values
        X_volatility_scaled = self.volatility_scaler.fit_transform(X_volatility)
        
        # Risk 데이터 준비 (5년, 16개 특성)
        risk_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility', 'MACD', 'BB_Position', 'Momentum_5',
                        'RSI_x_Volume', 'Trend_Strength', 'BB_Momentum', 'Volatility_x_RSI', 'MACD_x_Volume', 'Price_Momentum', 'RSI_MACD', 'BB_Volatility']
        X_risk = risk_data[risk_features].values
        y_risk = risk_data['Risk'].values
        X_risk_scaled = self.risk_scaler.fit_transform(X_risk)
        
        print(f"   ✅ 데이터 준비 완료:")
        print(f"     - Direction: {X_direction_scaled.shape[1]}개 특성, {len(direction_data)}개 샘플 (6년)")
        print(f"     - Volatility: {X_volatility_scaled.shape[1]}개 특성, {len(volatility_data)}개 샘플 (2년)")
        print(f"     - Risk: {X_risk_scaled.shape[1]}개 특성, {len(risk_data)}개 샘플 (5년)")
        
        return (X_direction_scaled, X_volatility_scaled, X_risk_scaled), (y_direction, y_volatility, y_risk)
    
    def build_models(self):
        """모델 구축"""
        print("6. 모델 구축...")
        
        # Direction: 8개 특성, LogisticRegression (6년 데이터 최적화)
        self.direction_model = LogisticRegression(
            C=0.1, penalty='l1', class_weight='balanced', 
            random_state=42, solver='liblinear'
        )
        
        # Volatility: 5개 특성, LogisticRegression (2년 데이터 최적화)
        self.volatility_model = LogisticRegression(
            C=0.01, penalty='l1', class_weight='balanced', 
            random_state=42, solver='liblinear'
        )
        
        # Risk: 16개 특성, StackingClassifier (5년 데이터 최적화)
        base_models = [
            ('logistic', LogisticRegression(C=0.1, penalty='l1', class_weight='balanced', random_state=42, solver='liblinear')),
            ('rf_shallow', RandomForestClassifier(max_depth=3, class_weight='balanced', random_state=42, n_jobs=-1))
        ]
        
        self.risk_model = StackingClassifier(
            estimators=base_models,
            final_estimator=LogisticRegression(random_state=42, max_iter=1000, class_weight='balanced'),
            cv=3,
            n_jobs=-1
        )
        
        print("   ✅ 모델 구축 완료")
    
    def train_models(self, X_data, y_data):
        """모델 훈련"""
        print("7. 모델 훈련...")
        start_time = time.time()
        
        X_direction, X_volatility, X_risk = X_data
        y_direction, y_volatility, y_risk = y_data
        
        # 각 모델 훈련
        print("   📊 Direction 모델 훈련 중...")
        self.direction_model.fit(X_direction, y_direction)
        
        print("   📊 Volatility 모델 훈련 중...")
        self.volatility_model.fit(X_volatility, y_volatility)
        
        print("   📊 Risk 모델 훈련 중...")
        self.risk_model.fit(X_risk, y_risk)
        
        training_time = time.time() - start_time
        print(f"   ✅ 모델 훈련 완료: {training_time:.1f}초")
        
        return training_time
    
    def save_models(self):
        """모델 저장"""
        print("8. 모델 저장...")
        
        # 저장할 모델 데이터 구성
        model_data = {
            'direction_model': self.direction_model,
            'volatility_model': self.volatility_model,
            'risk_model': self.risk_model,
            'direction_scaler': self.direction_scaler,
            'volatility_scaler': self.volatility_scaler,
            'risk_scaler': self.risk_scaler,
            'model_info': {
                'direction': {
                    'data_period': '6y',
                    'features': 8,
                    'description': 'Direction prediction (6년 데이터, 8개 특성)'
                },
                'volatility': {
                    'data_period': '2y',
                    'features': 5,
                    'description': 'Volatility prediction (2년 데이터, 5개 특성)'
                },
                'risk': {
                    'data_period': '5y',
                    'features': 16,
                    'description': 'Risk prediction (5년 데이터, 16개 특성)'
                }
            },
            'last_updated': time.time()
        }
        
        # PKL 파일로 저장
        with open('final_hybrid_optimal_models.pkl', 'wb') as f:
            pickle.dump(model_data, f)
        
        print("   ✅ 모델 저장 완료: final_hybrid_optimal_models.pkl")
        print("   📊 저장된 내용:")
        print("     - Direction 모델 (6년 데이터, 8개 특성)")
        print("     - Volatility 모델 (2년 데이터, 5개 특성)")
        print("     - Risk 모델 (5년 데이터, 16개 특성)")
        print("     - 각 모델별 스케일러")
        print("     - 모델 정보 및 업데이트 시간")
    
    def run_weekly_training(self):
        """주간 모델 재학습 실행"""
        print("=" * 80)
        print("🔄 주간 모델 재학습 시스템 실행")
        print("=" * 80)
        
        try:
            # 1. 모델별 최적 데이터 수집
            direction_stocks, volatility_stocks, risk_stocks = self.collect_optimal_data()
            
            # 2. 저렴한 주식 필터링 (150,000원 이하)
            all_tickers = list(set(direction_stocks + volatility_stocks + risk_stocks))
            affordable_stocks = []
            
            for ticker in all_tickers:
                try:
                    data = yf.download(ticker, period='1d', progress=False)
                    if not data.empty:
                        if isinstance(data.columns, pd.MultiIndex):
                            data.columns = data.columns.droplevel(1)
                        current_price = float(data['Close'].iloc[-1])
                        if current_price <= 150000:
                            affordable_stocks.append(ticker)
                except:
                    continue
            
            print(f"   📈 저렴한 주식: {len(affordable_stocks)}개")
            
            # 3. 모델별 특성 및 타겟 생성
            direction_data = self.create_direction_features_and_targets(affordable_stocks)
            volatility_data = self.create_volatility_features_and_targets(affordable_stocks)
            risk_data = self.create_risk_features_and_targets(affordable_stocks)
            
            # 4. 데이터 준비
            X_data, y_data = self.prepare_data(direction_data, volatility_data, risk_data)
            
            # 5. 모델 구축
            self.build_models()
            
            # 6. 모델 훈련
            training_time = self.train_models(X_data, y_data)
            
            # 7. 모델 저장
            self.save_models()
            
            print(f"\n✅ 주간 모델 재학습 완료!")
            print(f"⏰ 총 실행 시간: {training_time:.1f}초")
            
            return True
            
        except Exception as e:
            print(f"❌ 주간 모델 재학습 실패: {e}")
            import traceback
            traceback.print_exc()
            return False

def main():
    """메인 실행 함수"""
    trainer = WeeklyTrainer()
    success = trainer.run_weekly_training()
    
    if success:
        print("\n🎉 주간 모델 재학습 성공!")
    else:
        print("\n❌ 주간 모델 재학습 실패!")

if __name__ == "__main__":
    main()

