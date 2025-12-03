"""
매일 실행되는 일일 예측 시스템
- 오늘의 최신 데이터로 내일 예측
- today_predictions.json 생성
"""

import numpy as np
import pandas as pd
import yfinance as yf
import pickle
import json
from datetime import datetime, timedelta
import warnings
warnings.filterwarnings('ignore')

class DailyPredictor:
    def __init__(self):
        self.models = {}
        self.scalers = {}
        self.korean_tickers = [
            '005930.KS', '000660.KS', '051910.KS', '035420.KS', '035720.KS',
            '005380.KS', '000270.KS', '068270.KS', '207940.KS', '005490.KS',
            '006400.KS', '051900.KS', '028260.KS', '012330.KS', '066570.KS',
            '003550.KS', '096770.KS', '017670.KS', '009150.KS', '034730.KS',
            '000720.KS', '003490.KS', '011200.KS', '012450.KS', '015760.KS',
            '016360.KS', '017800.KS', '018880.KS', '020150.KS', '021240.KS',
        ]
        
    def load_models(self):
        """저장된 모델과 스케일러 로드"""
        print("📦 모델 로드 중...")
        try:
            with open('final_hybrid_optimal_models.pkl', 'rb') as f:
                model_data = pickle.load(f)
            
            self.models = {
                'direction': model_data['direction_model'],
                'volatility': model_data['volatility_model'],
                'risk': model_data['risk_model']
            }
            
            self.scalers = {
                'direction': model_data['direction_scaler'],
                'volatility': model_data['volatility_scaler'],
                'risk': model_data['risk_scaler']
            }
            
            print("✅ 모델 로드 완료!")
            return True
        except Exception as e:
            print(f"❌ 모델 로드 실패: {e}")
            return False
    
    def calculate_technical_indicators(self, df):
        """기술적 지표 계산"""
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
    
    def predict_stock(self, ticker):
        """종목 예측"""
        try:
            # 최근 30일 데이터 수집
            data = yf.download(ticker, period='1mo', progress=False)
            if data.empty:
                return None
            
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            
            df = self.calculate_technical_indicators(data)
            df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
            df = df.replace([np.inf, -np.inf], 0)
            
            # Direction 예측
            direction_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility', 'MACD', 'BB_Position', 'Momentum_5']
            X_dir = df[direction_features].iloc[-1:].values
            X_dir_scaled = self.scalers['direction'].transform(X_dir)
            direction_pred = self.models['direction'].predict(X_dir_scaled)[0]
            direction_proba = self.models['direction'].predict_proba(X_dir_scaled)[0][1]
            
            # Volatility 예측
            volatility_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility']
            X_vol = df[volatility_features].iloc[-1:].values
            X_vol_scaled = self.scalers['volatility'].transform(X_vol)
            volatility_pred = self.models['volatility'].predict(X_vol_scaled)[0]
            volatility_proba = self.models['volatility'].predict_proba(X_vol_scaled)[0][1]
            
            # Risk 예측
            risk_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility', 'MACD', 'BB_Position', 'Momentum_5',
                            'RSI_x_Volume', 'Trend_Strength', 'BB_Momentum', 'Volatility_x_RSI',
                            'MACD_x_Volume', 'Price_Momentum', 'RSI_MACD', 'BB_Volatility']
            
            # 고급 특성 계산
            df['RSI_x_Volume'] = df['RSI'] * df['Volume_Ratio']
            df['Trend_Strength'] = df['MA_Ratio'] * df['Momentum_5']
            df['BB_Momentum'] = df['BB_Position'] * df['Momentum_5']
            df['Volatility_x_RSI'] = df['Volatility'] * df['RSI']
            df['MACD_x_Volume'] = df['MACD'] * df['Volume_Ratio']
            df['Price_Momentum'] = df['Price_Change'] * df['Momentum_5']
            df['RSI_MACD'] = df['RSI'] * df['MACD']
            df['BB_Volatility'] = df['BB_Position'] * df['Volatility']
            
            X_risk = df[risk_features].iloc[-1:].values
            X_risk_scaled = self.scalers['risk'].transform(X_risk)
            risk_pred = self.models['risk'].predict(X_risk_scaled)[0]
            risk_proba = self.models['risk'].predict_proba(X_risk_scaled)[0][1]
            
            current_price = float(df['Close'].iloc[-1])
            
            return {
                'ticker': ticker,
                'currentPrice': current_price,
                'direction': {'prediction': int(direction_pred), 'probability': float(direction_proba)},
                'volatility': {'prediction': int(volatility_pred), 'probability': float(volatility_proba)},
                'risk': {'prediction': int(risk_pred), 'probability': float(risk_proba)}
            }
            
        except Exception as e:
            print(f"예측 실패 ({ticker}): {e}")
            return None
    
    def run_daily_prediction(self):
        """일일 예측 실행"""
        print("="*80)
        print("🚀 일일 예측 시스템 실행")
        print("="*80)
        
        # 모델 로드
        if not self.load_models():
            return
        
        # 예측 실행
        print(f"\n📊 {len(self.korean_tickers)}개 종목 예측 중...")
        predictions = {}
        
        for i, ticker in enumerate(self.korean_tickers, 1):
            print(f"   {i}/{len(self.korean_tickers)}: {ticker}...", end=' ')
            pred = self.predict_stock(ticker)
            if pred:
                predictions[ticker] = pred
                print("✅")
            else:
                print("❌")
        
        # 결과 저장
        result = {
            'date': datetime.now().strftime('%Y-%m-%d'),
            'timestamp': datetime.now().isoformat(),
            'totalStocks': len(predictions),
            'predictions': predictions
        }
        
        with open('today_predictions.json', 'w', encoding='utf-8') as f:
            json.dump(result, f, ensure_ascii=False, indent=2)
        
        print(f"\n✅ 저장 완료: today_predictions.json")
        print(f"📊 총 {len(predictions)}개 종목 예측 완료")

def main():
    predictor = DailyPredictor()
    predictor.run_daily_prediction()

if __name__ == "__main__":
    main()

