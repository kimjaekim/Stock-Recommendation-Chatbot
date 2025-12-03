"""
멀티 타임프레임 스마트 챗봇
- 12개 모델 (Direction/Volatility/Risk × 1/3/5/10일) 활용
- 자연어 이해 및 다양한 질문 유형 대응
- 타임프레임 자동 감지
"""

import numpy as np
import pandas as pd
import yfinance as yf
import pickle
import re
import sys
from pathlib import Path
from datetime import datetime

# 루트 디렉토리를 sys.path에 추가
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from utils.data_utils import load_or_download_macro_data, merge_macro_features
from utils.stock_name_mapping import STOCK_NAME_MAPPING

class MultiTimeframeChatbot:
    def __init__(self, silent=False):
        """12개 모델 로드"""
        if not silent:
            print("🤖 멀티 타임프레임 챗봇 초기화 중...")
        
        model_path = ROOT_DIR / 'core' / 'final_multi_timeframe_models.pkl'
        with open(model_path, 'rb') as f:
            data = pickle.load(f)
        
        self.models = data['models']
        self.scalers = data['scalers']
        self.pcas = data.get('pcas', {})
        self.performance = data['performance']
        self.medians = data['medians']
        self.macro_data = load_or_download_macro_data()
        
        # pykrx 데이터 로드
        try:
            pykrx_path = ROOT_DIR / 'data' / 'pykrx_data_30stocks_cache.pkl'
            with open(pykrx_path, 'rb') as f:
                cache = pickle.load(f)
            self.pykrx_data = cache['data']
        except:
            self.pykrx_data = {}
        
        # 역매핑 (한글 이름 → 티커)
        self.name_to_ticker = {name: ticker for ticker, name in STOCK_NAME_MAPPING.items()}
        
        # 별칭 추가
        self.aliases = {
            '삼성': '005930.KS',
            '하이닉스': '000660.KS',
            '엘지': '051910.KS',
            '네이버': '035420.KS',
            '카톡': '035720.KS',
            '현차': '005380.KS',
        }
        
        if not silent:
            print(f"✅ 로드 완료: {len(self.models)}개 모델")
            print(f"✅ 지원 종목: {len(STOCK_NAME_MAPPING)}개")
    
    def detect_timeframe(self, message):
        """타임프레임 자동 감지"""
        message = message.lower()
        
        # 명시적 지정
        if '1일' in message or '내일' in message or '오늘' in message:
            return '1day'
        elif '3일' in message:
            return '3day'
        elif '5일' in message or '이번주' in message or '일주일' in message:
            return '5day'
        elif '10일' in message or '다음주' in message or '2주' in message:
            return '10day'
        
        # 기본값
        return '5day'
    
    def extract_stock(self, message):
        """종목명 추출"""
        # 티커 직접 입력
        ticker_match = re.search(r'(\d{6}\.KS)', message)
        if ticker_match:
            return ticker_match.group(1)
        
        # 한글 종목명 검색
        for name, ticker in self.name_to_ticker.items():
            if name in message:
                return ticker
        
        # 별칭 검색
        for alias, ticker in self.aliases.items():
            if alias in message:
                return ticker
        
        return None
    
    def extract_multiple_stocks(self, message):
        """여러 종목 추출 (비교용)"""
        stocks = []
        
        # vs, 대, vs. 등으로 구분
        if ' vs ' in message.lower() or ' 대 ' in message or ' vs. ' in message:
            parts = re.split(r' vs\.?| 대 ', message, flags=re.IGNORECASE)
            for part in parts:
                ticker = self.extract_stock(part)
                if ticker:
                    stocks.append(ticker)
        
        return stocks if len(stocks) >= 2 else None
    
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
    
    def predict_stock(self, ticker, timeframe):
        """종목 예측"""
        try:
            data = yf.download(ticker, period='1mo', progress=False)
            if data.empty:
                return None
            
            if isinstance(data.columns, pd.MultiIndex):
                data.columns = data.columns.droplevel(1)
            
            df = self.calculate_technical_indicators(data)
            df = merge_macro_features(df, self.macro_data)
            
            # pykrx 병합
            if ticker in self.pykrx_data:
                from utils.data_utils import merge_pykrx_features
                df = merge_pykrx_features(df, self.pykrx_data, ticker)
            else:
                # pykrx 없으면 기본값
                df['Institution_Ratio'] = 0.33
                df['Foreign_Ratio'] = 0.33
                df['Individual_Ratio'] = 0.34
            
            # 상호작용 features
            df['RSI_x_Volume'] = df['RSI'] * df['Volume_Ratio']
            df['Trend_Strength'] = df['MA_Ratio'] * df['Momentum_5']
            df['BB_Momentum'] = df['BB_Position'] * df['Momentum_5']
            df['Volatility_x_RSI'] = df['Volatility'] * df['RSI']
            df['MACD_x_Volume'] = df['MACD'] * df['Volume_Ratio']
            df['Price_Momentum'] = df['Price_Change'] * df['Momentum_5']
            df['RSI_MACD'] = df['RSI'] * df['MACD']
            df['BB_Volatility'] = df['BB_Position'] * df['Volatility']
            
            df = df.fillna(method='ffill').fillna(method='bfill').fillna(0)
            df = df.replace([np.inf, -np.inf], 0)
            
            # Direction (13개)
            dir_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility', 
                           'MACD', 'BB_Position', 'Momentum_5',
                           'KOSPI_Change', 'USD_KRW_Change', 'VIX', 'VIX_Change', 'SP500_Change']
            
            X_dir = df[dir_features].iloc[-1:].values
            X_dir_scaled = self.scalers[f'direction_{timeframe}'].transform(X_dir)
            X_dir_pca = self.pcas[f'direction_{timeframe}'].transform(X_dir_scaled)
            
            dir_pred = self.models[f'direction_{timeframe}'].predict(X_dir_pca)[0]
            dir_proba = self.models[f'direction_{timeframe}'].predict_proba(X_dir_pca)[0][1]
            
            # Volatility (8개: 기술 5 + pykrx 3)
            vol_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility',
                           'Institution_Ratio', 'Foreign_Ratio', 'Individual_Ratio']
            X_vol = df[vol_features].iloc[-1:].values
            X_vol_scaled = self.scalers[f'volatility_{timeframe}'].transform(X_vol)
            
            vol_pred = self.models[f'volatility_{timeframe}'].predict(X_vol_scaled)[0]
            vol_proba = self.models[f'volatility_{timeframe}'].predict_proba(X_vol_scaled)[0][1]
            
            # Risk (16개: 기술 8 + 상호작용 8)
            risk_features = ['MA_Ratio', 'RSI', 'Price_Change', 'Volume_Ratio', 'Volatility', 
                            'MACD', 'BB_Position', 'Momentum_5',
                            'RSI_x_Volume', 'Trend_Strength', 'BB_Momentum', 'Volatility_x_RSI',
                            'MACD_x_Volume', 'Price_Momentum', 'RSI_MACD', 'BB_Volatility']
            X_risk = df[risk_features].iloc[-1:].values
            X_risk_scaled = self.scalers[f'risk_{timeframe}'].transform(X_risk)
            
            risk_pred = self.models[f'risk_{timeframe}'].predict(X_risk_scaled)[0]
            risk_proba = self.models[f'risk_{timeframe}'].predict_proba(X_risk_scaled)[0][1]
            
            # 종합 점수 계산
            score = self.calculate_score(dir_pred, dir_proba, vol_pred, vol_proba, risk_pred, risk_proba)
            
            current_price = float(df['Close'].iloc[-1])
            
            return {
                'ticker': ticker,
                'name': STOCK_NAME_MAPPING.get(ticker, ticker),
                'timeframe': timeframe,
                'direction': {'pred': dir_pred, 'prob': dir_proba},
                'volatility': {'pred': vol_pred, 'prob': vol_proba},
                'risk': {'pred': risk_pred, 'prob': risk_proba},
                'score': score,
                'price': current_price,
                'accuracy': self.performance[f'direction_{timeframe}']['test_acc']
            }
        
        except Exception as e:
            print(f"예측 실패: {e}")
            return None
    
    def calculate_score(self, dir_pred, dir_prob, vol_pred, vol_prob, risk_pred, risk_prob):
        """종합 점수 계산"""
        # Direction 신호
        dir_signal = (dir_pred * 2 - 1) * dir_prob
        
        # Volatility 신호 (낮음=+1)
        vol_signal = -(vol_pred * 2 - 1) * vol_prob
        
        # Risk 신호 (안전=+1)
        risk_signal = -(risk_pred * 2 - 1) * risk_prob
        
        # 가중치
        score = 0.35 * dir_signal + 0.40 * vol_signal + 0.25 * risk_signal
        
        return score
    
    def get_recommendation(self, score):
        """추천 등급"""
        if score >= 0.3:
            return {'grade': '강력 매수', 'emoji': '🚀', 'action': 'STRONG_BUY'}
        elif score >= 0.1:
            return {'grade': '매수', 'emoji': '📈', 'action': 'BUY'}
        elif score >= -0.1:
            return {'grade': '보유', 'emoji': '⏸️', 'action': 'HOLD'}
        elif score >= -0.3:
            return {'grade': '매도', 'emoji': '📉', 'action': 'SELL'}
        else:
            return {'grade': '강력 매도', 'emoji': '🔻', 'action': 'STRONG_SELL'}
    
    def rank_all_stocks(self, timeframe):
        """전체 종목 순위"""
        results = []
        for ticker in STOCK_NAME_MAPPING.keys():
            pred = self.predict_stock(ticker, timeframe)
            if pred:
                results.append(pred)
        
        results.sort(key=lambda x: x['score'], reverse=True)
        return results
    
    def response_single_stock(self, ticker, timeframe):
        """단일 종목 분석 응답"""
        pred = self.predict_stock(ticker, timeframe)
        if not pred:
            return "❌ 종목 분석에 실패했습니다."
        
        tf_korean = {'1day': '내일', '3day': '3일 후', '5day': '5일 후', '10day': '10일 후'}
        rec = self.get_recommendation(pred['score'])
        
        response = f"📊 **{pred['name']}** ({tf_korean[timeframe]} 예측)\n\n"
        response += f"[개별 예측]\n"
        response += f"  방향성: {'상승' if pred['direction']['pred'] == 1 else '하락'} (확률: {pred['direction']['prob']:.1%})\n"
        response += f"  변동성: {'높음' if pred['volatility']['pred'] == 1 else '낮음'} (확률: {pred['volatility']['prob']:.1%})\n"
        response += f"  위험도: {'위험' if pred['risk']['pred'] == 1 else '안전'} (확률: {pred['risk']['prob']:.1%})\n\n"
        
        response += f"[종합 분석]\n"
        response += f"  {rec['emoji']} **{rec['grade']}**\n"
        response += f"  투자 점수: {pred['score']:+.3f} / ±1.00\n\n"
        
        response += f"[기본 정보]\n"
        response += f"  현재가: {pred['price']:,.0f}원\n"
        response += f"  모델 정확도: {pred['accuracy']:.1%}\n"
        
        return response
    
    def response_top_stocks(self, timeframe, top_n=5):
        """추천 종목 순위 응답"""
        tf_korean = {'1day': '내일', '3day': '3일 후', '5day': '이번주', '10day': '다음주'}
        
        response = f"🏆 **{tf_korean[timeframe]} 투자 추천 TOP {top_n}**\n\n"
        
        results = self.rank_all_stocks(timeframe)
        
        for i, pred in enumerate(results[:top_n], 1):
            rec = self.get_recommendation(pred['score'])
            response += f"{i}. **{pred['name']}** {rec['emoji']}\n"
            response += f"   점수: {pred['score']:+.3f} | 현재가: {pred['price']:,.0f}원\n"
            response += f"   상승: {pred['direction']['prob']:.0%} | 변동성: {'낮음' if pred['volatility']['pred'] == 0 else '높음'}\n\n"
        
        return response
    
    def response_comparison(self, ticker1, ticker2, timeframe):
        """종목 비교 응답"""
        pred1 = self.predict_stock(ticker1, timeframe)
        pred2 = self.predict_stock(ticker2, timeframe)
        
        if not pred1 or not pred2:
            return "❌ 종목 분석에 실패했습니다."
        
        tf_korean = {'1day': '내일', '3day': '3일 후', '5day': '5일 후', '10day': '10일 후'}
        
        response = f"⚖️ **종목 비교** ({tf_korean[timeframe]})\n\n"
        
        for i, pred in enumerate([pred1, pred2], 1):
            rec = self.get_recommendation(pred['score'])
            response += f"{'🔵' if i == 1 else '🔴'} **{pred['name']}**\n"
            response += f"   추천: {rec['emoji']} {rec['grade']} (점수: {pred['score']:+.3f})\n"
            response += f"   상승 확률: {pred['direction']['prob']:.1%}\n"
            response += f"   현재가: {pred['price']:,.0f}원\n\n"
        
        # 결론
        winner = pred1 if pred1['score'] > pred2['score'] else pred2
        response += f"💡 **결론:** {winner['name']}이(가) 더 유망합니다!\n"
        
        return response
    
    def response_risky_stocks(self, timeframe):
        """위험 종목 응답"""
        results = self.rank_all_stocks(timeframe)
        risky = [r for r in results if r['score'] < -0.2][:5]
        
        if not risky:
            return "✅ 현재 특별히 위험한 종목은 없습니다."
        
        response = f"⚠️ **매도 고려 종목 (위험도 높음)**\n\n"
        
        for i, pred in enumerate(risky, 1):
            rec = self.get_recommendation(pred['score'])
            response += f"{i}. **{pred['name']}** {rec['emoji']}\n"
            response += f"   점수: {pred['score']:+.3f} | 위험: {pred['risk']['prob']:.0%}\n\n"
        
        return response
    
    def chat(self, message):
        """메인 챗봇 로직"""
        message_lower = message.lower()
        
        # 타임프레임 감지
        timeframe = self.detect_timeframe(message)
        
        # 1. 비교 요청
        stocks = self.extract_multiple_stocks(message)
        if stocks:
            return self.response_comparison(stocks[0], stocks[1], timeframe)
        
        # 2. 위험 종목 요청
        if any(word in message_lower for word in ['위험', '매도', '피해야', '조심']):
            return self.response_risky_stocks(timeframe)
        
        # 3. 추천 순위 요청
        if any(word in message_lower for word in ['추천', '순위', '좋은', '어떤', '뭐']):
            ticker = self.extract_stock(message)
            if not ticker:
                return self.response_top_stocks(timeframe)
        
        # 4. 단일 종목 분석
        ticker = self.extract_stock(message)
        if ticker:
            return self.response_single_stock(ticker, timeframe)
        
        # 5. 기본 응답
        return self.help_message()
    
    def help_message(self):
        """도움말"""
        return """🤖 **안전한 낚시터 챗봇 사용법**

질문 예시:
1. "내일 삼성전자 어때?" - 단일 종목 분석
2. "이번주 추천 종목은?" - TOP 5 추천
3. "삼성전자 vs SK하이닉스" - 종목 비교
4. "위험한 종목은?" - 매도 고려 종목
5. "다음주 NAVER 분석해줘" - 특정 기간 분석

지원 기간: 내일(1일), 3일 후, 이번주(5일), 다음주(10일)
지원 종목: 30개 (삼성전자, SK하이닉스, LG화학 등)
"""


def main():
    """테스트"""
    print("="*80)
    print("💬 멀티 타임프레임 챗봇 테스트")
    print("="*80)
    
    chatbot = MultiTimeframeChatbot()
    
    test_messages = [
        "내일 삼성전자 어때?",
        "이번주 추천 종목은?",
        "삼성전자 vs SK하이닉스",
        "위험한 종목은?",
        "다음주 네이버 분석해줘"
    ]
    
    for msg in test_messages:
        print(f"\n{'='*80}")
        print(f"👤 사용자: {msg}")
        print(f"{'='*80}")
        response = chatbot.chat(msg)
        print(f"🤖 챗봇:\n{response}")


if __name__ == "__main__":
    main()

