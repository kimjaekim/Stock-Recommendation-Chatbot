"""
멀티 타임프레임 일일 예측
12개 모델로 today_predictions_<timeframe>.json 생성
"""

import json
import sys
from pathlib import Path
from datetime import datetime

# 루트 디렉토리를 sys.path에 추가
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

from core.multi_timeframe_chatbot import MultiTimeframeChatbot
from utils.stock_name_mapping import STOCK_NAME_MAPPING

# 커맨드 라인 인자로 타임프레임 받기
if len(sys.argv) > 1:
    TIMEFRAME = sys.argv[1]
else:
    TIMEFRAME = '5day'

print("="*80)
print(f"🚀 멀티 타임프레임 일일 예측 시스템 - {TIMEFRAME}")
print("="*80)

# 챗봇 초기화
print("\n[1/3] 챗봇 초기화 중...")
chatbot = MultiTimeframeChatbot(silent=False)

# 30개 종목
tickers = list(STOCK_NAME_MAPPING.keys())

print(f"\n[2/3] {len(tickers)}개 종목 예측 중...")
predictions = {}

for i, ticker in enumerate(tickers, 1):
    name = STOCK_NAME_MAPPING[ticker]
    print(f"   {i}/{len(tickers)}: {name} ({ticker})...", end=' ')
    
    try:
        pred = chatbot.predict_stock(ticker, TIMEFRAME)
        
        if pred:
            predictions[ticker] = {
                'ticker': str(ticker),
                'stockName': str(name),
                'currentPrice': float(pred['price']),
                'direction': {
                    'prediction': int(pred['direction']['pred']),
                    'probability': float(pred['direction']['prob'])
                },
                'volatility': {
                    'prediction': int(pred['volatility']['pred']),
                    'probability': float(pred['volatility']['prob'])
                },
                'risk': {
                    'prediction': int(pred['risk']['pred']),
                    'probability': float(pred['risk']['prob'])
                },
                'score': float(pred['score']),
                'recommendation': str(chatbot.get_recommendation(pred['score'])['grade']),
                'timeframe': str(TIMEFRAME),
                'accuracy': float(pred['accuracy'])
            }
            print("✅")
        else:
            print("❌ 실패")
    except Exception as e:
        print(f"❌ {e}")

print(f"\n[3/3] 결과 저장 중...")

# 날짜 설정
from datetime import timedelta
prediction_date = datetime.now().strftime('%Y-%m-%d')  # 예측 생성 날짜

# 타겟 날짜 계산 (예측 대상 날짜)
if TIMEFRAME == '1day':
    target_days = 1
elif TIMEFRAME == '3day':
    target_days = 3
elif TIMEFRAME == '5day':
    target_days = 5
elif TIMEFRAME == '10day':
    target_days = 10
else:
    target_days = 1

target_date = (datetime.now() + timedelta(days=target_days)).strftime('%Y-%m-%d')

# 결과 저장
result = {
    'prediction_date': prediction_date,  # 예측 생성 날짜
    'target_date': target_date,          # 예측 대상 날짜
    'date': prediction_date,             # 하위 호환성
    'timestamp': datetime.now().isoformat(),
    'timeframe': TIMEFRAME,
    'totalStocks': len(predictions),
    'modelType': 'multi_timeframe_12_models',
    'predictions': predictions
}

# 예측 결과 저장 폴더
predictions_dir = ROOT_DIR / 'predictions'
predictions_dir.mkdir(exist_ok=True)

# 날짜별 파일명 (검증용)
filename_dated = f'predictions_{TIMEFRAME}_{prediction_date}.json'
# 하위 호환성 파일명 (챗봇용)
filename_legacy = f'today_predictions_{TIMEFRAME}.json'

# 날짜별 파일 저장
with open(predictions_dir / filename_dated, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

# 하위 호환성 파일 저장
with open(predictions_dir / filename_legacy, 'w', encoding='utf-8') as f:
    json.dump(result, f, ensure_ascii=False, indent=2)

print(f"✅ 저장 완료:")
print(f"   - 날짜별: {predictions_dir / filename_dated}")
print(f"   - 호환용: {predictions_dir / filename_legacy}")

# 통계
safe_count = sum(1 for p in predictions.values() if p['risk']['prediction'] == 0)
upward_count = sum(1 for p in predictions.values() if p['direction']['prediction'] == 1)
low_vol_count = sum(1 for p in predictions.values() if p['volatility']['prediction'] == 0)

print("\n" + "="*80)
print("📊 예측 통계")
print("="*80)
print(f"총 종목: {len(predictions)}개")
print(f"안전 종목: {safe_count}개 ({safe_count/len(predictions)*100:.1f}%)")
print(f"상승 예상: {upward_count}개 ({upward_count/len(predictions)*100:.1f}%)")
print(f"저변동성: {low_vol_count}개 ({low_vol_count/len(predictions)*100:.1f}%)")

# Top 5
sorted_stocks = sorted(predictions.values(), key=lambda x: x['score'], reverse=True)
print(f"\n🏆 TOP 5 추천 종목:")
for i, stock in enumerate(sorted_stocks[:5], 1):
    print(f"  {i}. {stock['stockName']}: {stock['recommendation']} (점수: {stock['score']:+.3f})")

print("\n" + "="*80)
print("✅ 완료!")
print("="*80)

