# 📁 파일 폴더 구조 재구성 계획

## 🗂️ 제안된 폴더 구조

```
jusic_data/
├── 📚 docs/                          # 문서 파일
│   ├── README.md
│   ├── QUICK_START_GUIDE.md
│   ├── SYSTEM_OPERATION_GUIDE.md
│   ├── FILE_DESCRIPTION.md
│   └── MODEL_OPTIMIZATION_RESULTS.md
│
├── 🎯 core/                          # 핵심 모델 및 챗봇
│   ├── final_multi_timeframe_models.pkl
│   ├── multi_timeframe_chatbot.py
│   └── chatbot_cli.py
│
├── 🚀 scripts/                       # 실행 스크립트
│   ├── predict_daily_multitf.py
│   ├── run_all_predictions.bat
│   ├── run_all_predictions.py
│   └── test_chatbot.bat
│
├── 🛠️ utils/                         # 유틸리티
│   ├── data_utils.py
│   ├── stock_name_mapping.py
│   └── sentiment_keywords.py
│
├── 🔬 experiments/                   # 실험/연구용
│   ├── final_hybrid_optimal_system.py
│   ├── train_hybrid_system.py
│   ├── predict_daily.py
│   └── chat_response_logic.py
│
├── 📊 analysis/                      # 분석/검증
│   ├── evaluate_models.py
│   ├── verify_today_predictions.py
│   ├── print_model_structure.py
│   └── print_model_metrics.py
│
├── 📁 data/                          # 데이터 파일
│   ├── pykrx_data_30stocks_cache.pkl
│   └── cached_data/                  # (기존 폴더)
│
├── 📈 predictions/                   # 예측 결과
│   ├── today_predictions_1day.json
│   ├── today_predictions_3day.json
│   ├── today_predictions_5day.json
│   ├── today_predictions_10day.json
│   └── predictions_*_*.json
│
├── 📋 reports/                       # 리포트
│   ├── model_performance_report.csv
│   ├── model_performance_report.json
│   └── perf_history/                 # (기존 폴더)
│
├── 🔧 tools/                         # 도구
│   ├── naver_news_api.py
│   └── news_collector.py
│
└── ⚙️ config/                        # 설정
    └── requirements.txt
```

## ⚠️ 주의사항

폴더 구조 변경 시 import 경로 수정이 필요합니다:
- `from data_utils import ...` → `from utils.data_utils import ...`
- `from stock_name_mapping import ...` → `from utils.stock_name_mapping import ...`
- `from multi_timeframe_chatbot import ...` → `from core.multi_timeframe_chatbot import ...`

또는 모든 스크립트를 루트에서 실행하도록 sys.path 조정 필요.

## 💡 대안: 현재 구조 유지 + 문서만 정리

import 경로 수정이 복잡할 수 있으므로, 현재 구조를 유지하고 문서만 정리하는 것을 권장합니다.

