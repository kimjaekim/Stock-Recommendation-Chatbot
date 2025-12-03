"""
오늘의 예측 vs 실제 결과 검증
어제 예측한 파일을 읽어 오늘 실제 결과와 비교
"""

import yfinance as yf
import json
from datetime import datetime, timedelta
import sys
import os
import glob

def get_realtime_verification():
    """실시간 예측 검증 - 챗봇 추천 상위 3개 종목만"""
    
    # 1. 1일 전 날짜 계산 (내일 예측 → 오늘 검증)
    PREDICTION_DAYS = 1  # 1일 예측 사용
    days_ago = (datetime.now() - timedelta(days=PREDICTION_DAYS)).strftime('%Y-%m-%d')
    today = datetime.now().strftime('%Y-%m-%d')
    
    # 2. 어제 예측한 파일 찾기 (1day 예측 파일)
    prediction_file = f'predictions_1day_{days_ago}.json'
    
    # 파일이 없으면 최신 파일로 fallback (테스트용)
    if not os.path.exists(prediction_file):
        # print(f"[WARNING] Yesterday prediction file({prediction_file}) not found. Finding latest file...")
        prediction_file = 'today_predictions_1day.json'
        
        if not os.path.exists(prediction_file):
            # 최신 predictions_1day 파일 찾기
            files = glob.glob('predictions_1day_*.json')
            if files:
                prediction_file = max(files)  # 가장 최신 파일
                # print(f"[INFO] Using latest file: {prediction_file}")
            else:
                return {
                    'error': f'예측 파일을 찾을 수 없습니다.',
                    'recommendations': [],
                    'accuracy': 0
                }
    
    # 3. 예측 파일 불러오기
    try:
        with open(prediction_file, 'r', encoding='utf-8') as f:
            predictions = json.load(f)
        
        file_prediction_date = predictions.get('prediction_date', 'unknown')
        file_target_date = predictions.get('target_date', 'unknown')
        # print(f"[OK] File loaded: {prediction_file}")
        # print(f"   Prediction date: {file_prediction_date}")
        # print(f"   Target date: {file_target_date}")
        # print(f"   Verification date: {today}")
    except Exception as e:
        return {
            'error': f'예측 파일 로드 실패: {str(e)}',
            'recommendations': [],
            'accuracy': 0,
            'prediction_file': prediction_file
        }
    
    # 2. 추천 종목 선별 (안전 + 상승 예측 + 확률 높은 순)
    recommended_stocks = []
    for ticker, pred in predictions['predictions'].items():
        direction = pred['direction']['prediction']
        risk = pred['risk']['prediction']
        volatility = pred['volatility']['prediction']
        
        # 상승 확률 계산
        if direction == 1:
            upward_prob = pred['direction']['probability']
        else:
            upward_prob = 1 - pred['direction']['probability']
        
        # 추천 점수 계산 (안전 + 상승 + 확률)
        recommendation_score = 0
        if direction == 1:  # 상승 예측
            recommendation_score += 100
        if risk == 0:  # 안전
            recommendation_score += 50
        if volatility == 0:  # 저변동
            recommendation_score += 30
        recommendation_score += upward_prob * 100  # 확률 가중치
        
        recommended_stocks.append({
            'ticker': ticker,
            'stockName': pred['stockName'],
            'score': float(recommendation_score),
            'direction': direction,
            'risk': risk,
            'volatility': volatility,
            'upward_prob': float(upward_prob),
            'predicted_direction': '상승' if direction == 1 else '하락'
        })
    
    # 3. 상위 3개 선별 (점수 높은 순)
    recommended_stocks.sort(key=lambda x: x['score'], reverse=True)
    top_3 = recommended_stocks[:3]
    
    results = {
        'recommendations': [],
        'accuracy': 0,
        'timestamp': datetime.now().isoformat(),
        'total_return': 0.0,
        'avg_return': 0.0,
        'prediction_date': file_prediction_date,  # 예측 생성일
        'target_date': file_target_date,          # 예측 대상일
        'verification_date': today,                # 검증 날짜
        'prediction_file': prediction_file         # 사용한 파일
    }
    
    # 4. 상위 3개 종목만 실시간 가격 확인
    success_count = 0
    total_return = 0.0
    
    for stock_info in top_3:
        ticker = stock_info['ticker']
        try:
            stock = yf.Ticker(ticker)
            
            # 오늘 데이터 (1분봉)
            today_data = stock.history(period='1d', interval='1m')
            
            if len(today_data) == 0:
                # 장 마감 또는 데이터 없음 - 현재가 사용
                pred = predictions['predictions'][ticker]
                result_data = {
                    'rank': len(results['recommendations']) + 1,
                    'ticker': ticker,
                    'stockName': stock_info['stockName'],
                    'predicted_direction': stock_info['predicted_direction'],
                    'predicted_prob': float(stock_info['upward_prob'] * 100),
                    'recommendation_score': stock_info['score'],
                    'actual_change': 0.0,
                    'actual_direction': '대기중',
                    'start_price': float(pred['currentPrice']),
                    'current_price': float(pred['currentPrice']),
                    'is_correct': None,
                    'status': '장 마감'
                }
                results['recommendations'].append(result_data)
                continue
            
            # 시작가와 현재가
            start_price = float(today_data['Open'].iloc[0])
            current_price = float(today_data['Close'].iloc[-1])
            
            # 실제 변화율
            actual_change = ((current_price - start_price) / start_price) * 100
            actual_direction = 1 if actual_change > 0 else 0
            
            # 예측 vs 실제 비교
            is_correct = (stock_info['direction'] == actual_direction)
            
            if is_correct:
                success_count += 1
            
            total_return += actual_change
            
            result_data = {
                'rank': len(results['recommendations']) + 1,
                'ticker': ticker,
                'stockName': stock_info['stockName'],
                'predicted_direction': stock_info['predicted_direction'],
                'predicted_prob': float(stock_info['upward_prob'] * 100),
                'recommendation_score': stock_info['score'],
                'actual_change': float(actual_change),
                'actual_direction': '상승' if actual_direction == 1 else '하락',
                'start_price': float(start_price),
                'current_price': float(current_price),
                'is_correct': bool(is_correct),
                'status': '✅ 성공' if is_correct else '❌ 실패'
            }
            
            results['recommendations'].append(result_data)
                
        except Exception as e:
            result_data = {
                'rank': len(results['recommendations']) + 1,
                'ticker': ticker,
                'stockName': stock_info['stockName'],
                'predicted_direction': stock_info['predicted_direction'],
                'predicted_prob': float(stock_info['upward_prob'] * 100),
                'recommendation_score': stock_info['score'],
                'actual_change': 0.0,
                'actual_direction': '오류',
                'start_price': 0.0,
                'current_price': 0.0,
                'is_correct': None,
                'status': f'오류: {str(e)}'
            }
            results['recommendations'].append(result_data)
    
    # 5. 정확도 및 수익률 계산
    valid_count = sum(1 for r in results['recommendations'] if r['is_correct'] is not None)
    if valid_count > 0:
        results['accuracy'] = float((success_count / valid_count) * 100)
        results['total_return'] = float(total_return)
        results['avg_return'] = float(total_return / valid_count)
    else:
        results['accuracy'] = 0.0
        results['total_return'] = 0.0
        results['avg_return'] = 0.0
    
    return results


if __name__ == '__main__':
    # Windows에서 UTF-8 출력 강제 설정
    import io
    if sys.platform == 'win32':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        sys.stderr = open('nul', 'w')
    else:
        sys.stderr = open('/dev/null', 'w')
    
    results = get_realtime_verification()
    
    # JSON 출력
    print(json.dumps(results, ensure_ascii=False, indent=2))

