# 파일들을 폴더별로 정리하는 PowerShell 스크립트

$baseDir = $PSScriptRoot

# 문서 파일
Move-Item -Path "$baseDir\README.md" -Destination "$baseDir\docs\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\QUICK_START_GUIDE.md" -Destination "$baseDir\docs\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\SYSTEM_OPERATION_GUIDE.md" -Destination "$baseDir\docs\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\FILE_DESCRIPTION.md" -Destination "$baseDir\docs\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\MODEL_OPTIMIZATION_RESULTS.md" -Destination "$baseDir\docs\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\ORGANIZE_PLAN.md" -Destination "$baseDir\docs\" -ErrorAction SilentlyContinue

# 핵심 파일
Move-Item -Path "$baseDir\final_multi_timeframe_models.pkl" -Destination "$baseDir\core\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\multi_timeframe_chatbot.py" -Destination "$baseDir\core\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\chatbot_cli.py" -Destination "$baseDir\core\" -ErrorAction SilentlyContinue

# 스크립트 파일
Move-Item -Path "$baseDir\predict_daily_multitf.py" -Destination "$baseDir\scripts\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\run_all_predictions.bat" -Destination "$baseDir\scripts\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\run_all_predictions.py" -Destination "$baseDir\scripts\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\test_chatbot.bat" -Destination "$baseDir\scripts\" -ErrorAction SilentlyContinue

# 유틸리티
Move-Item -Path "$baseDir\data_utils.py" -Destination "$baseDir\utils\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\stock_name_mapping.py" -Destination "$baseDir\utils\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\sentiment_keywords.py" -Destination "$baseDir\utils\" -ErrorAction SilentlyContinue

# 실험 파일
Move-Item -Path "$baseDir\final_hybrid_optimal_system.py" -Destination "$baseDir\experiments\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\train_hybrid_system.py" -Destination "$baseDir\experiments\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\predict_daily.py" -Destination "$baseDir\experiments\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\chat_response_logic.py" -Destination "$baseDir\experiments\" -ErrorAction SilentlyContinue

# 분석 파일
Move-Item -Path "$baseDir\evaluate_models.py" -Destination "$baseDir\analysis\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\verify_today_predictions.py" -Destination "$baseDir\analysis\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\print_model_structure.py" -Destination "$baseDir\analysis\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\print_model_metrics.py" -Destination "$baseDir\analysis\" -ErrorAction SilentlyContinue

# 데이터 파일
Move-Item -Path "$baseDir\pykrx_data_30stocks_cache.pkl" -Destination "$baseDir\data\" -ErrorAction SilentlyContinue

# 예측 결과
Get-ChildItem "$baseDir\today_predictions_*.json" | Move-Item -Destination "$baseDir\predictions\" -ErrorAction SilentlyContinue
Get-ChildItem "$baseDir\predictions_*_*.json" | Move-Item -Destination "$baseDir\predictions\" -ErrorAction SilentlyContinue

# 리포트
Move-Item -Path "$baseDir\model_performance_report.csv" -Destination "$baseDir\reports\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\model_performance_report.json" -Destination "$baseDir\reports\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\perf_history" -Destination "$baseDir\reports\" -ErrorAction SilentlyContinue

# 도구
Move-Item -Path "$baseDir\naver_news_api.py" -Destination "$baseDir\tools\" -ErrorAction SilentlyContinue
Move-Item -Path "$baseDir\news_collector.py" -Destination "$baseDir\tools\" -ErrorAction SilentlyContinue

# 설정
Move-Item -Path "$baseDir\requirements.txt" -Destination "$baseDir\config\" -ErrorAction SilentlyContinue

Write-Host "파일 정리 완료!"

