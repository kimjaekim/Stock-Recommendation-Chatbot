# 📁 폴더 구조 설명

## 현재 구조

```
jusic_data/
├── 📚 docs/                          # 문서 파일
│   ├── README.md                     # 프로젝트 개요
│   ├── QUICK_START_GUIDE.md         # 빠른 시작 가이드
│   ├── SYSTEM_OPERATION_GUIDE.md    # 운영 가이드
│   ├── FILE_DESCRIPTION.md          # 파일 설명
│   └── MODEL_OPTIMIZATION_RESULTS.md # 모델 최적화 결과
│
├── 🎯 core/                          # 핵심 모델 및 챗봇
│   ├── final_multi_timeframe_models.pkl  # 메인 모델 (12개)
│   ├── multi_timeframe_chatbot.py   # 챗봇 엔진
│   └── chatbot_cli.py               # Spring Boot 연동 CLI
│
├── 🚀 scripts/                       # 실행 스크립트
│   ├── predict_daily_multitf.py     # 일일 예측 생성
│   ├── run_all_predictions.bat      # 배치 파일 (모든 타임프레임)
│   ├── run_all_predictions.py       # Python 스크립트
│   └── test_chatbot.bat             # 챗봇 테스트
│
├── 🛠️ utils/                         # 유틸리티
│   ├── data_utils.py                # 데이터 처리 유틸리티
│   ├── stock_name_mapping.py        # 종목 매핑
│   └── sentiment_keywords.py        # 감성 키워드
│
├── 🔬 experiments/                   # 실험/연구용 (구버전)
│   ├── final_hybrid_optimal_system.py
│   ├── train_hybrid_system.py
│   ├── predict_daily.py
│   └── chat_response_logic.py
│
├── 📊 analysis/                      # 분석/검증
│   ├── evaluate_models.py           # 모델 성능 평가
│   ├── verify_today_predictions.py  # 예측 검증
│   ├── print_model_structure.py     # 모델 구조 출력
│   └── print_model_metrics.py       # 성능 지표 출력
│
├── 📁 data/                          # 데이터 파일
│   ├── pykrx_data_30stocks_cache.pkl
│   └── cached_data/                 # 캐시 폴더
│
├── 📈 predictions/                   # 예측 결과
│   ├── today_predictions_1day.json
│   ├── today_predictions_3day.json
│   ├── today_predictions_5day.json
│   ├── today_predictions_10day.json
│   └── predictions_*_*.json         # 날짜별 백업
│
├── 📋 reports/                       # 리포트
│   ├── model_performance_report.csv
│   ├── model_performance_report.json
│   └── perf_history/                # 성능 히스토리
│
├── 🔧 tools/                         # 도구
│   ├── naver_news_api.py
│   └── news_collector.py
│
└── ⚙️ config/                        # 설정
    └── requirements.txt
```

## 실행 방법

### 예측 생성
```bash
cd C:\tools\spring_dev\workspace_boot\jusic_data
py -3 scripts\predict_daily_multitf.py 1day
```

또는 배치 파일:
```bash
scripts\run_all_predictions.bat
```

### 챗봇 테스트
```bash
py -3 core\chatbot_cli.py "내일 삼성전자 어때?"
```

또는 배치 파일:
```bash
scripts\test_chatbot.bat
```

## 중요 참고사항

- **모든 스크립트는 루트 디렉토리(`jusic_data/`)에서 실행해야 합니다**
- import 경로는 자동으로 조정됩니다 (`sys.path`에 루트 추가)
- 파일 경로는 `Path(__file__).parent.parent`를 사용하여 루트 기준으로 설정됩니다

