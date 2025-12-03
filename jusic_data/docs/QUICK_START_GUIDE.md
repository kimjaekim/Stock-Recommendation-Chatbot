# 🚀 빠른 시작 가이드 (Quick Start Guide)

## 📋 사전 요구사항

### 1. Python 환경
- Python 3.8 이상 필요
- 권장: Python 3.9 이상

### 2. 필수 패키지 설치

```bash
# 프로젝트 루트에서 실행
cd C:\tools\spring_dev\workspace_boot\jusic_data

# 방법 1: requirements.txt 사용 (권장)
pip install -r requirements.txt

# 방법 2: 개별 설치
pip install pandas numpy scikit-learn yfinance pykrx plotly
```

**설치할 패키지 목록:**
- `pandas` - 데이터 처리
- `numpy` - 수치 계산
- `scikit-learn` - 머신러닝 모델
- `yfinance` - 주가 데이터 수집 (Yahoo Finance)
- `pykrx` - 한국 주식 데이터 수집 (외국인/기관 거래)
- `plotly` - 시각화 (선택사항)

**참고:** `requirements.txt` 파일에 모든 패키지가 정리되어 있습니다.

### 3. 필수 파일 확인

다음 파일들이 있는지 확인하세요:
- ✅ `final_multi_timeframe_models.pkl` - 메인 모델 파일 (627KB)
- ✅ `pykrx_data_30stocks_cache.pkl` - pykrx 캐시 (4.4MB)
- ✅ `stock_name_mapping.py` - 종목 매핑
- ✅ `data_utils.py` - 데이터 유틸리티

---

## 🎯 빠른 실행

### 1단계: 일일 예측 생성 (가장 먼저 해야 할 일)

**목적**: 오늘의 예측 결과를 생성하여 JSON 파일로 저장

#### 방법 1: 개별 타임프레임 실행
```bash
cd C:\tools\spring_dev\workspace_boot\jusic_data

# 1일 예측 생성
py -3 predict_daily_multitf.py 1day

# 3일 예측 생성
py -3 predict_daily_multitf.py 3day

# 5일 예측 생성
py -3 predict_daily_multitf.py 5day

# 10일 예측 생성
py -3 predict_daily_multitf.py 10day
```

#### 방법 2: 배치 파일로 한번에 실행 (권장)
```bash
# Windows에서 배치 파일 실행
cd C:\tools\spring_dev\workspace_boot\jusic_data
run_all_predictions.bat
```

**또는 더블클릭:**
- `run_all_predictions.bat` 파일을 더블클릭하면 자동으로 모든 타임프레임 예측이 생성됩니다.

#### 방법 3: 수동으로 한번에 실행
```bash
# Windows PowerShell에서
cd C:\tools\spring_dev\workspace_boot\jusic_data
py -3 predict_daily_multitf.py 1day
py -3 predict_daily_multitf.py 3day
py -3 predict_daily_multitf.py 5day
py -3 predict_daily_multitf.py 10day
```

**결과 파일:**
- `today_predictions_1day.json`
- `today_predictions_3day.json`
- `today_predictions_5day.json`
- `today_predictions_10day.json`
- `predictions_1day_YYYY-MM-DD.json` (날짜별 백업)

**예상 소요 시간:** 각 타임프레임당 약 1-2분 (30개 종목 예측)

---

### 2단계: 챗봇 테스트

**목적**: 챗봇이 정상 작동하는지 확인

#### 방법 1: Python에서 직접 테스트
```bash
cd C:\tools\spring_dev\workspace_boot\jusic_data

py -3 -c "from multi_timeframe_chatbot import MultiTimeframeChatbot; bot = MultiTimeframeChatbot(); print(bot.chat('내일 삼성전자 어때?'))"
```

#### 방법 2: 배치 파일로 테스트
```bash
# Windows에서 배치 파일 실행
test_chatbot.bat
```

#### 방법 3: Python 스크립트로 테스트
새 파일 `test_chatbot.py` 생성:
```python
from multi_timeframe_chatbot import MultiTimeframeChatbot

bot = MultiTimeframeChatbot()

# 테스트 메시지들
test_messages = [
    "내일 삼성전자 어때?",
    "이번주 추천 종목은?",
    "삼성전자 vs SK하이닉스",
    "다음주 NAVER 분석해줘"
]

for msg in test_messages:
    print(f"\n{'='*60}")
    print(f"사용자: {msg}")
    print(f"{'='*60}")
    response = bot.chat(msg)
    print(response)
```

실행:
```bash
py -3 test_chatbot.py
```

---

### 3단계: Spring Boot 연동 테스트

**목적**: Spring Boot에서 Python 챗봇 호출 테스트

#### CLI로 테스트
```bash
cd C:\tools\spring_dev\workspace_boot\jusic_data

# 단일 메시지 테스트
py -3 chatbot_cli.py "내일 삼성전자 어때?"

# JSON 응답 확인
py -3 chatbot_cli.py "이번주 추천 종목은?"
```

**예상 출력 (JSON 형식):**
```json
{
  "success": true,
  "message": "📊 **삼성전자** (이번주 예측)...",
  "timeframe": "5day",
  "recommendations": [...],
  "chartData": {...}
}
```

---

## 📅 정기 운영 스케줄

### 매일 (장 마감 후, 오후 6시)

**작업**: 모든 타임프레임 예측 생성

#### 방법 1: 배치 파일 사용 (가장 간단)
```bash
cd C:\tools\spring_dev\workspace_boot\jusic_data
run_all_predictions.bat
```

#### 방법 2: 개별 실행
```bash
cd C:\tools\spring_dev\workspace_boot\jusic_data

py -3 predict_daily_multitf.py 1day
py -3 predict_daily_multitf.py 3day
py -3 predict_daily_multitf.py 5day
py -3 predict_daily_multitf.py 10day
```

**자동화 방법 (Windows Task Scheduler):**
1. 작업 스케줄러 열기
2. 기본 작업 만들기
3. 트리거: 매일 오후 6시
4. 작업: 프로그램 시작
   - 프로그램: `C:\tools\spring_dev\workspace_boot\jusic_data\run_all_predictions.bat`
   - 또는 Python 직접 실행:
     - 프로그램: `C:\Users\사용자명\AppData\Local\Programs\Python\Python311\python.exe`
     - 인수: `-3 C:\tools\spring_dev\workspace_boot\jusic_data\run_all_predictions.py` (Python 스크립트 버전 사용 시)
     - 시작 위치: `C:\tools\spring_dev\workspace_boot\jusic_data`

---

## 🔍 문제 해결

### 1. 모델 파일을 찾을 수 없습니다

**에러 메시지:**
```
FileNotFoundError: final_multi_timeframe_models.pkl
```

**해결 방법:**
```bash
# 현재 디렉토리 확인
cd C:\tools\spring_dev\workspace_boot\jusic_data
dir final_multi_timeframe_models.pkl
```

파일이 없으면 모델 파일을 다른 곳에서 복사하거나, 시스템 관리자에게 문의하세요.

---

### 2. 패키지를 찾을 수 없습니다

**에러 메시지:**
```
ModuleNotFoundError: No module named 'yfinance'
```

**해결 방법:**
```bash
# 패키지 설치
pip install yfinance pandas numpy scikit-learn
```

---

### 3. 데이터 수집 실패

**에러 메시지:**
```
yfinance 실패: [에러 메시지]
```

**해결 방법:**
1. 인터넷 연결 확인
2. yfinance API 제한 확인 (너무 빠르게 요청하면 일시 차단 가능)
3. 잠시 후 재시도

---

### 4. Python 명령어 인식 안 됨

**에러 메시지:**
```
'python'은(는) 내부 또는 외부 명령, 실행할 수 있는 프로그램, 또는 배치 파일이 아닙니다.
```

**해결 방법:**
Windows에서는 `python` 대신 `py -3` 사용:
```bash
py -3 predict_daily_multitf.py 1day
```

또는 Python 전체 경로 사용:
```bash
C:\Users\사용자명\AppData\Local\Programs\Python\Python311\python.exe predict_daily_multitf.py 1day
```

---

## 🧪 실행 확인 체크리스트

실행이 성공했는지 확인하는 체크리스트:

- [ ] 예측 파일 생성 확인
  - `today_predictions_1day.json` 존재
  - `today_predictions_3day.json` 존재
  - `today_predictions_5day.json` 존재
  - `today_predictions_10day.json` 존재

- [ ] 파일 크기 확인
  - 각 JSON 파일이 0KB가 아님
  - 파일 내용에 `predictions` 키가 있음

- [ ] 챗봇 응답 확인
  - "내일 삼성전자 어때?" 질문에 답변 나옴
  - JSON 형식 응답 정상

---

## 📝 실행 예시

### 예시 1: 일일 예측 생성

```bash
C:\tools\spring_dev\workspace_boot\jusic_data> py -3 predict_daily_multitf.py 5day

================================================================================
🚀 멀티 타임프레임 일일 예측 시스템 - 5day
================================================================================

[1/3] 챗봇 초기화 중...
🤖 멀티 타임프레임 챗봇 초기화 중...
✅ 로드 완료: 12개 모델
✅ 지원 종목: 30개

[2/3] 30개 종목 예측 중...
   1/30: 삼성전자 (005930.KS)... ✅
   2/30: SK하이닉스 (000660.KS)... ✅
   ...
   
[3/3] 결과 저장 중...
✅ 저장 완료:
   - 날짜별: predictions_5day_2025-10-31.json
   - 호환용: today_predictions_5day.json

================================================================================
📊 예측 통계
================================================================================
총 종목: 30개
안전 종목: 12개 (40.0%)
상승 예상: 18개 (60.0%)
저변동성: 15개 (50.0%)

🏆 TOP 5 추천 종목:
  1. 삼성전자: 매수 (점수: +0.245)
  2. SK하이닉스: 매수 (점수: +0.198)
  ...

================================================================================
✅ 완료!
================================================================================
```

### 예시 2: 챗봇 테스트

```bash
C:\tools\spring_dev\workspace_boot\jusic_data> py -3 chatbot_cli.py "내일 삼성전자 어때?"

{"success":true,"message":"📊 **삼성전자** (내일 예측)\n\n[개별 예측]\n  방향성: 상승 (확률: 52.3%)\n  변동성: 낮음 (확률: 48.1%)\n  위험도: 위험 (확률: 75.2%)\n\n[종합 분석]\n  ⏸️ **보유**\n  투자 점수: -0.123 / ±1.00\n\n[기본 정보]\n  현재가: 104,100원\n  모델 정확도: 51.7%","timeframe":"1day"}
```

---

## 🎓 고급 사용법

### 1. 특정 타임프레임만 예측 생성
```bash
# 1일 예측만 생성
py -3 predict_daily_multitf.py 1day
```

### 2. 챗봇 직접 사용 (Python 코드)
```python
from multi_timeframe_chatbot import MultiTimeframeChatbot

# 챗봇 초기화
bot = MultiTimeframeChatbot()

# 종목 분석
result = bot.predict_stock('005930.KS', '5day')
print(result)

# 전체 종목 순위
rankings = bot.rank_all_stocks('10day')
for i, stock in enumerate(rankings[:10], 1):
    print(f"{i}. {stock['name']}: {stock['score']:.3f}")
```

### 3. 모델 성능 확인
```bash
# 모델 구조 및 성능 확인
py -3 print_model_structure.py

# 성능 지표 확인
py -3 print_model_metrics.py

# 상세 성능 평가 (재계산)
py -3 evaluate_models.py
```

---

## 🆘 도움이 필요하신가요?

### 자주 묻는 질문

**Q: 예측 파일이 생성되지 않아요**
- A: 모델 파일(`final_multi_timeframe_models.pkl`)이 있는지 확인하세요.
- A: 인터넷 연결을 확인하세요 (주가 데이터 수집 필요).

**Q: 챗봇이 응답하지 않아요**
- A: 먼저 예측 파일(`today_predictions_*.json`)이 생성되어 있는지 확인하세요.
- A: Python 버전이 3.8 이상인지 확인하세요.

**Q: Spring Boot에서 Python 호출이 안 돼요**
- A: `chatbot_cli.py`가 정상 작동하는지 먼저 테스트하세요.
- A: Python 경로가 올바른지 확인하세요.

---

## 📦 배치 파일 및 스크립트

프로젝트에 포함된 편의 스크립트:

- **`run_all_predictions.bat`** - Windows 배치 파일 (모든 타임프레임 예측 생성)
- **`run_all_predictions.py`** - Python 스크립트 버전
- **`test_chatbot.bat`** - 챗봇 테스트 배치 파일
- **`requirements.txt`** - 필수 패키지 목록

**사용법:**
```bash
# 배치 파일 실행 (Windows)
run_all_predictions.bat

# Python 스크립트 실행
py -3 run_all_predictions.py

# 챗봇 테스트
test_chatbot.bat
```

---

## ✅ 다음 단계

1. ✅ 예측 파일 생성 성공 확인
2. ✅ 챗봇 응답 정상 확인
3. 📱 Spring Boot 서버 연동 (`chatbot_cli.py` 사용)
4. 🌐 프론트엔드 개발
5. 📊 모니터링 시스템 구축

---

## 📚 추가 문서

더 자세한 정보는 다음 문서를 참고하세요:

- **`SYSTEM_OPERATION_GUIDE.md`** - 상세 운영 가이드
- **`FILE_DESCRIPTION.md`** - 파일 구조 및 용도 설명
- **`README.md`** - 프로젝트 개요
- **`MODEL_OPTIMIZATION_RESULTS.md`** - 모델 최적화 실험 결과

---

**축하합니다! 시스템 실행 준비가 완료되었습니다! 🎉**

**빠른 시작:**
1. `pip install -r requirements.txt` 실행
2. `run_all_predictions.bat` 더블클릭
3. `test_chatbot.bat` 실행하여 챗봇 테스트

