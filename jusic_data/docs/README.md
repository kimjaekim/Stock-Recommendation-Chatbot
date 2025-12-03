# 안전한 낚시터 AI - 주식 예측/추천 시스템

## 📦 폴더 구조 (jusic_data)

- `final_multi_timeframe_models.pkl`  
  👉 1,3,5,10일 × (방향/변동성/위험) 12개 예측모델 통합 저장, 실 서비스 예측에 사용
- `final_hybrid_optimal_system.py`  
  👉 단일 최적화 하이브리드 시스템(단일기간, 상세 experiment/분석용)
- `multi_timeframe_chatbot.py`  
  👉 1/3/5/10일 챗봇 자연어 분석, 모델 자동 선택, 다이내믹 추천 백엔드
- `chatbot_cli.py`  
  👉 Spring Boot(JAVA)와 연동되는 CLI 래퍼, 입출력 json포맷 변환 포함
- `predict_daily_multitf.py`  
  👉 멀티 타임프레임 예측 결과 json생성 자동화 스크립트 (실서비스)
- `predict_daily.py`  
  👉 구버전 단일 타임프레임 예측 시스템 (실험용)
- `today_predictions_1day.json`/`3day.json`/`5day.json`/`10day.json`  
  👉 오늘 생성된 각 기간별 예측결과 json(서비스 API/프론트엔드 직접 사용)
- `predictions_1day_YYYY-MM-DD.json` 등  
  👉 특정 날짜 예측 결과(실제 시장 검증/오늘의 예측 vs 실제 비교)
- `verify_today_predictions.py`  
  👉 실제 시장 데이터/상위 추천 검증 스크립트(추천 hit률 자동 검증)
- `train_hybrid_system.py`  
  👉 구버전 하이브리드 모델 재학습 (실험용)
- `SYSTEM_OPERATION_GUIDE.md`  
  👉 시스템 전체 운영 매뉴얼/자동화 흐름/배치 및 서비스 연동 설명
- `MODEL_OPTIMIZATION_RESULTS.md`  
  👉 각 실험별(피처 조합, 기간, 하이퍼파라미터 등) tuning 결과 정리
- `data_utils.py`/`stock_name_mapping.py`/`sentiment_keywords.py` 등
  👉 공통 유틸리티, 티커-이름매핑, 감성 키워드 등 보조 스크립트
- `chat_response_logic.py`  
  👉 구버전 챗봇 응답 로직 (현재는 `multi_timeframe_chatbot.py` 사용)
- `naver_news_api.py`, `news_collector.py`  
  👉 감성분석뉴스/네이버 API 데이터 수집기, 케싱
- `pykrx_data_30stocks_cache.pkl`, `cached_data/`  
  👉 외부 데이터(macro, pykrx, 뉴스감성, etc) 캐시/재활용 파일

## 🧑‍💻 **실서비스 운영 구조**
1. (Python) 멀티 타임프레임 모델 예측 json 자동 생성 → (`today_predictions_1day/3day/5day/10day.json`)
2. (Spring Boot) REST API에서 json불러와 자연어/투자 추천 처리
3. (프론트) 기간별 버튼/분석/챗봇 기반 실시간 안내 (1일/3일/5일/10일 선택 가능)
4. (배치) 모델 재학습 (필요시 수동 실행)
5. (검증) `verify_today_predictions.py`로 매일 대표 추천 결과 실제시장과 비교

## 📝 **시작방법 요약**
- 데이터 최신화: `predict_daily_multitf.py` 스케줄 실행 (자동/수동)
- 서버 연동: chatbot_cli.py 등으로 Spring Boot와 연결, 자연어 입력 처리 가능
- 포트폴리오/백테스팅/추천 스코어링 등 확장 가능 구조

## 📑 기타
- 최상위 주요 코드/결과/json 이외 캐시는 cached_data/에 보관
- 모델 구조, 하이퍼파라미터, 각 기간 피처조합 상세 및 실험 내역은 MODEL_OPTIMIZATION_RESULTS.md 참고
