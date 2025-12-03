# 📁 jusic_data 폴더 파일 정리

## 🤖 **실서비스 핵심 파일**

### 모델 파일
- **`final_multi_timeframe_models.pkl`** (627KB)
  - 12개 예측 모델 통합 저장 파일 (1/3/5/10일 × Direction/Volatility/Risk)
  - 실서비스 예측에 직접 사용되는 메인 모델 번들
  - 저장 내용: 모델, 스케일러, PCA, 성능 지표, 중앙값 등

### 챗봇 시스템
- **`multi_timeframe_chatbot.py`** (17KB, 424줄)
  - 멀티 타임프레임 스마트 챗봇 메인 파일
  - 12개 모델 로드 및 자연어 처리
  - 타임프레임 자동 감지, 종목 분석, 추천 등

- **`chatbot_cli.py`** (5KB, 145줄)
  - Spring Boot와 연동되는 CLI 래퍼
  - JSON 형식 입출력 변환
  - 외부 시스템 연동용 인터페이스

### 예측 생성 시스템
- **`predict_daily_multitf.py`** (4.6KB, 139줄)
  - 멀티 타임프레임 일일 예측 자동화
  - 커맨드라인 인자로 타임프레임(1/3/5/10일) 받아 예측 실행
  - `today_predictions_<timeframe>.json` 파일 생성

- **`predict_daily.py`** (10KB, 266줄)
  - 구버전 일일 예측 시스템
  - `final_hybrid_optimal_models.pkl` 사용 (단일 타임프레임)
  - `today_predictions.json` 생성

### 검증/분석 시스템
- **`verify_today_predictions.py`** (8.5KB, 221줄)
  - 오늘의 예측 vs 실제 결과 검증
  - 추천 종목의 실제 시장 성과 비교
  - Hit률 자동 계산

- **`evaluate_models.py`** (11KB, 300줄)
  - 모델 성능 평가 스크립트
  - Train/Val/Test 지표 재계산
  - `model_performance_report.csv/json` 생성

- **`print_model_structure.py`** (9.7KB, 265줄)
  - PKL 파일 구조 및 모델 정보 출력
  - 모델 타입, 파라미터, 성능 지표 확인용

- **`print_model_metrics.py`** (3.2KB, 94줄)
  - 모델 성능 지표 요약 출력
  - PKL 내부 성능 정보 확인용

---

## 🔬 **실험/연구용 파일**

- **`final_hybrid_optimal_system.py`** (49KB, 1050줄)
  - 단일 최적화 하이브리드 시스템
  - 실험 및 상세 분석용 (현재는 멀티타임프레임 사용)
  - `final_hybrid_optimal_models.pkl` 생성

- **`train_hybrid_system.py`** (21KB, 482줄)
  - 매주 실행되는 모델 재학습 시스템
  - 구버전 하이브리드 모델 재훈련용
  - `final_hybrid_optimal_models.pkl` 업데이트

---

## 🛠️ **유틸리티 파일**

- **`data_utils.py`** (9.9KB, 298줄)
  - 공통 데이터 유틸리티 함수
  - 거시경제 데이터 로드/병합
  - pykrx 데이터 로드/병합
  - 여러 파일에서 import하여 사용

- **`stock_name_mapping.py`** (1.5KB, 53줄)
  - 티커 ↔ 한글 종목명 매핑 딕셔너리
  - 30개 한국 주식 종목 정보

- **`chat_response_logic.py`** (8.3KB, 229줄)
  - 구버전 챗봇 응답 로직
  - `today_predictions.json` 기반 추천
  - 현재는 `multi_timeframe_chatbot.py` 사용

- **`sentiment_keywords.py`** (4.7KB, 149줄)
  - 감성 분석 키워드 정의
  - 뉴스 감성 분석에 사용

- **`naver_news_api.py`** (8.1KB, 233줄)
  - 네이버 뉴스 API 데이터 수집
  - 감성 분석용 뉴스 데이터 가져오기

- **`news_collector.py`** (8.9KB, 271줄)
  - 뉴스 수집기
  - 뉴스 데이터 캐싱 및 관리

---

## 📊 **데이터/캐시 파일**

### 모델 파일
- **`final_multi_timeframe_models.pkl`** - 메인 모델 번들 (627KB)

### 캐시 파일
- **`pykrx_data_30stocks_cache.pkl`** (4.4MB)
  - pykrx 데이터 캐시 (30개 종목)

### 캐시 폴더 (`cached_data/`)
- `macro_data.pkl` - 거시경제 데이터 캐시
- `naver_api_news_cache.pkl` - 네이버 뉴스 캐시
- `news_sentiment_cache.pkl` - 뉴스 감성 캐시
- `pykrx_data.pkl` - pykrx 데이터 캐시
- `real_news_sentiment_cache.pkl` - 실제 뉴스 감성 캐시
- `sentiment_simulation_cache.pkl` - 감성 시뮬레이션 캐시

### 예측 결과 JSON 파일
- **`today_predictions_1day.json`** - 오늘 생성된 1일 예측
- **`today_predictions_3day.json`** - 오늘 생성된 3일 예측
- **`today_predictions_5day.json`** - 오늘 생성된 5일 예측
- **`today_predictions_10day.json`** - 오늘 생성된 10일 예측
- **`predictions_1day_2025-10-31.json`** - 특정 날짜 예측 결과 (검증용)
- **`predictions_3day_2025-10-31.json`** - 특정 날짜 예측 결과
- **`predictions_5day_2025-10-31.json`** - 특정 날짜 예측 결과
- **`predictions_10day_2025-10-31.json`** - 특정 날짜 예측 결과

### 성능 리포트 파일
- **`model_performance_report.csv`** - 모델 성능 리포트 (CSV)
- **`model_performance_report.json`** - 모델 성능 리포트 (JSON)
- **`perf_history/`** - 성능 히스토리 저장 폴더
  - `model_performance_2025-10-31_02-59-22.csv/json`
  - `model_performance_2025-10-31_03-13-38.csv/json`

---

## 📚 **문서 파일**

- **`README.md`** (2.9KB, 49줄)
  - 프로젝트 개요 및 폴더 구조 설명

- **`SYSTEM_OPERATION_GUIDE.md`** (5.1KB, 169줄)
  - 시스템 전체 운영 매뉴얼
  - 자동화 흐름, 배치 실행, 서비스 연동 설명

- **`MODEL_OPTIMIZATION_RESULTS.md`** (6.9KB, 255줄)
  - 모델 최적화 실험 결과 정리
  - 피처 조합, 기간, 하이퍼파라미터 튜닝 내역

---

## 🗂️ **폴더 구조**

```
jusic_data/
├── 🤖 실서비스 파일
│   ├── final_multi_timeframe_models.pkl (메인 모델)
│   ├── multi_timeframe_chatbot.py (챗봇)
│   ├── chatbot_cli.py (Spring Boot 연동)
│   ├── predict_daily_multitf.py (예측 생성)
│   └── verify_today_predictions.py (검증)
│
├── 🔬 실험/연구 파일
│   ├── final_hybrid_optimal_system.py
│   └── train_hybrid_system.py
│
├── 🛠️ 유틸리티
│   ├── data_utils.py
│   ├── stock_name_mapping.py
│   ├── sentiment_keywords.py
│   ├── naver_news_api.py
│   └── news_collector.py
│
├── 📊 데이터/캐시
│   ├── pykrx_data_30stocks_cache.pkl
│   ├── cached_data/ (외부 데이터 캐시)
│   ├── today_predictions_*.json (오늘 예측)
│   ├── predictions_*_*.json (날짜별 예측)
│   ├── model_performance_report.* (성능 리포트)
│   └── perf_history/ (성능 히스토리)
│
├── 📚 문서
│   ├── README.md
│   ├── SYSTEM_OPERATION_GUIDE.md
│   └── MODEL_OPTIMIZATION_RESULTS.md
│
└── 🔍 분석 도구
    ├── evaluate_models.py
    ├── print_model_structure.py
    └── print_model_metrics.py
```

---

## 🎯 **파일 사용 현황**

### ✅ 현재 실서비스에서 사용 중
1. `final_multi_timeframe_models.pkl` - 메인 모델
2. `multi_timeframe_chatbot.py` - 챗봇 엔진
3. `chatbot_cli.py` - Spring Boot 연동
4. `predict_daily_multitf.py` - 일일 예측 생성
5. `data_utils.py` - 데이터 유틸리티
6. `stock_name_mapping.py` - 종목 매핑
7. `today_predictions_*.json` - 예측 결과

### ⚠️ 구버전/대체됨
- `predict_daily.py` - `predict_daily_multitf.py`로 대체
- `chat_response_logic.py` - `multi_timeframe_chatbot.py`로 대체
- `final_hybrid_optimal_system.py` - 실험용, 현재 미사용
- `train_hybrid_system.py` - 구버전 재학습, 현재 미사용

### 📊 분석/검증용
- `evaluate_models.py` - 성능 평가
- `verify_today_predictions.py` - 예측 검증
- `print_model_structure.py` - 구조 확인
- `print_model_metrics.py` - 지표 확인

