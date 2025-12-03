@echo off
chcp 65001 >nul
echo ========================================================================
echo 챗봇 테스트
echo ========================================================================
echo.

cd /d "%~dp0\.."

echo 테스트 1: 단일 종목 분석 (1일)
py -3 core\chatbot_cli.py "내일 삼성전자 어때?"
echo.
echo.

echo 테스트 2: 추천 종목 요청 (5일)
py -3 core\chatbot_cli.py "이번주 추천 종목은?"
echo.
echo.

echo 테스트 3: 종목 비교 (10일)
py -3 core\chatbot_cli.py "다음주 삼성전자 vs SK하이닉스"
echo.
echo.

echo ✅ 테스트 완료!
pause

