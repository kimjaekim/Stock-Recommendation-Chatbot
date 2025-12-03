"""
Spring Boot에서 호출 가능한 CLI 챗봇
"""

import sys
import json
import io
from pathlib import Path

# UTF-8 출력 설정 (Windows 환경 대응)
if sys.platform == 'win32':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')
    sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8', errors='replace')

# 루트 디렉토리를 sys.path에 추가
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.multi_timeframe_chatbot import MultiTimeframeChatbot

def extract_structured_data(chatbot, user_message, timeframe):
    """구조화된 데이터 추출 (차트용)"""
    message_lower = user_message.lower()
    
    # 추천 순위 요청인 경우
    if any(word in message_lower for word in ['추천', '순위', '좋은', '어떤', '뭐']):
        ticker = chatbot.extract_stock(user_message)
        if not ticker:  # 특정 종목이 아닌 전체 순위 요청
            results = chatbot.rank_all_stocks(timeframe)
            
            # 상위 5개
            top_5 = results[:5]
            
            # 차트 데이터 생성
            recommendations = []
            chart_labels = []
            chart_scores = []
            chart_colors = []
            
            for pred in top_5:
                rec = chatbot.get_recommendation(pred['score'])
                recommendations.append({
                    'ticker': str(pred['ticker']),
                    'name': str(pred['name']),
                    'score': float(pred['score']),
                    'recommendation': str(rec['grade']),
                    'emoji': str(rec['emoji']),
                    'price': float(pred['price']),
                    'directionProb': float(pred['direction']['prob']),
                    'volatilityPred': int(pred['volatility']['pred']),
                    'riskPred': int(pred['risk']['pred'])
                })
                
                chart_labels.append(str(pred['name']))
                chart_scores.append(float(round(pred['score'], 3)))
                
                # 점수에 따른 색상
                if pred['score'] >= 0.3:
                    chart_colors.append('#4caf50')  # 녹색
                elif pred['score'] >= 0.1:
                    chart_colors.append('#8bc34a')  # 연녹색
                elif pred['score'] >= -0.1:
                    chart_colors.append('#ff9800')  # 주황색
                else:
                    chart_colors.append('#f44336')  # 빨간색
            
            return {
                'recommendations': recommendations,
                'chartData': {
                    'labels': chart_labels,
                    'values': chart_scores,
                    'colors': chart_colors
                }
            }
    
    # 비교 요청인 경우
    stocks = chatbot.extract_multiple_stocks(user_message)
    if stocks:
        pred1 = chatbot.predict_stock(stocks[0], timeframe)
        pred2 = chatbot.predict_stock(stocks[1], timeframe)
        
        if pred1 and pred2:
            return {
                'comparison': {
                    'stock1': {
                        'name': str(pred1['name']),
                        'score': float(pred1['score']),
                        'directionProb': float(pred1['direction']['prob'])
                    },
                    'stock2': {
                        'name': str(pred2['name']),
                        'score': float(pred2['score']),
                        'directionProb': float(pred2['direction']['prob'])
                    }
                },
                'chartData': {
                    'labels': [str(pred1['name']), str(pred2['name'])],
                    'values': [float(pred1['score']), float(pred2['score'])],
                    'colors': ['#2196f3', '#f44336']
                }
            }
    
    return None

def main():
    if len(sys.argv) < 2:
        print(json.dumps({"error": "메시지를 입력하세요"}))
        sys.exit(1)
    
    user_message = sys.argv[1]
    
    try:
        # 챗봇 초기화 (모든 출력 억제)
        import warnings
        warnings.filterwarnings('ignore')
        
        # stderr 출력 완전히 억제 (Spring Boot용)
        import os
        if os.environ.get('SPRING_BOOT_MODE') != 'false':
            sys.stderr = open(os.devnull, 'w')
        
        chatbot = MultiTimeframeChatbot(silent=True)
        
        # 챗봇 응답 (stdout으로 JSON만 출력)
        response = chatbot.chat(user_message)
        
        # 타임프레임 정보
        timeframe = chatbot.detect_timeframe(user_message)
        
        # 구조화된 데이터 추출
        structured_data = extract_structured_data(chatbot, user_message, timeframe)
        
        # JSON 응답
        result = {
            "success": True,
            "message": response,
            "timeframe": timeframe
        }
        
        # 구조화된 데이터가 있으면 추가
        if structured_data:
            result.update(structured_data)
        
        print(json.dumps(result, ensure_ascii=False))
        
    except Exception as e:
        error_result = {
            "success": False,
            "error": str(e)
        }
        print(json.dumps(error_result, ensure_ascii=False))
        sys.exit(1)

if __name__ == "__main__":
    main()

