"""Import 및 경로 테스트"""
import sys
import io
from pathlib import Path

# UTF-8 출력 설정
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
sys.stderr = io.TextIOWrapper(sys.stderr.buffer, encoding='utf-8')

# 루트 디렉토리를 sys.path에 추가
ROOT_DIR = Path(__file__).parent
sys.path.insert(0, str(ROOT_DIR))

print("="*60)
print("테스트 1: Import 테스트")
print("="*60)

try:
    from core.multi_timeframe_chatbot import MultiTimeframeChatbot
    print("[OK] core.multi_timeframe_chatbot import 성공")
except Exception as e:
    print(f"[FAIL] core.multi_timeframe_chatbot import 실패: {e}")
    sys.exit(1)

try:
    from utils.data_utils import load_or_download_macro_data
    print("[OK] utils.data_utils import 성공")
except Exception as e:
    print(f"[FAIL] utils.data_utils import 실패: {e}")
    sys.exit(1)

try:
    from utils.stock_name_mapping import STOCK_NAME_MAPPING
    print("[OK] utils.stock_name_mapping import 성공")
except Exception as e:
    print(f"[FAIL] utils.stock_name_mapping import 실패: {e}")
    sys.exit(1)

print("\n" + "="*60)
print("테스트 2: 파일 경로 테스트")
print("="*60)

# 모델 파일 확인
model_path = ROOT_DIR / 'core' / 'final_multi_timeframe_models.pkl'
if model_path.exists():
    print(f"[OK] 모델 파일 존재: {model_path}")
else:
    print(f"[FAIL] 모델 파일 없음: {model_path}")
    sys.exit(1)

# pykrx 데이터 확인
pykrx_path = ROOT_DIR / 'data' / 'pykrx_data_30stocks_cache.pkl'
if pykrx_path.exists():
    print(f"[OK] pykrx 데이터 존재: {pykrx_path}")
else:
    print(f"[WARN] pykrx 데이터 없음 (선택사항): {pykrx_path}")

# 예측 파일 확인
predictions_dir = ROOT_DIR / 'predictions'
if predictions_dir.exists():
    json_files = list(predictions_dir.glob('today_predictions_*.json'))
    print(f"[OK] 예측 파일 {len(json_files)}개 존재: {predictions_dir}")
    for f in json_files[:4]:
        print(f"   - {f.name}")
else:
    print(f"[WARN] 예측 파일 폴더 없음 (실행 후 생성됨): {predictions_dir}")

print("\n" + "="*60)
print("테스트 3: 챗봇 초기화 테스트 (모델 로드)")
print("="*60)

try:
    print("챗봇 초기화 중... (시간이 걸릴 수 있습니다)")
    bot = MultiTimeframeChatbot(silent=True)
    print("[OK] 챗봇 초기화 성공!")
    print(f"   - 모델 수: {len(bot.models)}개")
    print(f"   - 지원 종목: {len(STOCK_NAME_MAPPING)}개")
except Exception as e:
    print(f"[FAIL] 챗봇 초기화 실패: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

print("\n" + "="*60)
print("[OK] 모든 테스트 통과!")
print("="*60)

