"""
모든 타임프레임 예측을 한번에 실행하는 스크립트
"""

import subprocess
import sys
from pathlib import Path

# 루트 디렉토리를 sys.path에 추가
ROOT_DIR = Path(__file__).parent.parent
sys.path.insert(0, str(ROOT_DIR))

TIMEFRAMES = ['1day', '3day', '5day', '10day']
SCRIPT_PATH = Path(__file__).parent / 'predict_daily_multitf.py'

def main():
    print("="*80)
    print("🚀 멀티 타임프레임 예측 생성 - 모든 타임프레임 실행")
    print("="*80)
    print()
    
    success_count = 0
    fail_count = 0
    
    for i, timeframe in enumerate(TIMEFRAMES, 1):
        print(f"[{i}/{len(TIMEFRAMES)}] {timeframe} 예측 생성 중...")
        print("-" * 80)
        
        try:
            result = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), timeframe],
                cwd=ROOT_DIR,  # 루트 디렉토리에서 실행
                capture_output=False,
                text=True,
                check=True
            )
            success_count += 1
            print(f"✅ {timeframe} 예측 완료!\n")
        except subprocess.CalledProcessError as e:
            fail_count += 1
            print(f"❌ {timeframe} 예측 실패: {e}\n")
        except Exception as e:
            fail_count += 1
            print(f"❌ {timeframe} 예측 오류: {e}\n")
    
    print("="*80)
    print("📊 실행 결과")
    print("="*80)
    print(f"성공: {success_count}개")
    print(f"실패: {fail_count}개")
    
    if fail_count == 0:
        print("\n✅ 모든 타임프레임 예측 생성 완료!")
        print("\n생성된 파일:")
        predictions_dir = ROOT_DIR / 'predictions'
        for tf in TIMEFRAMES:
            filename = f'today_predictions_{tf}.json'
            if (predictions_dir / filename).exists():
                print(f"  - {filename}")
    else:
        print(f"\n⚠️ 일부 타임프레임 예측이 실패했습니다.")
        sys.exit(1)

if __name__ == "__main__":
    main()

