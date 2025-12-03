@echo off
chcp 65001 >nul
echo ========================================================================
echo 멀티 타임프레임 예측 생성 - 모든 타임프레임 실행
echo ========================================================================
echo.

cd /d "%~dp0\.."

echo [1/4] 1일 예측 생성 중...
py -3 scripts\predict_daily_multitf.py 1day
if %errorlevel% neq 0 (
    echo ❌ 1일 예측 실패
    pause
    exit /b 1
)
echo.

echo [2/4] 3일 예측 생성 중...
py -3 scripts\predict_daily_multitf.py 3day
if %errorlevel% neq 0 (
    echo ❌ 3일 예측 실패
    pause
    exit /b 1
)
echo.

echo [3/4] 5일 예측 생성 중...
py -3 scripts\predict_daily_multitf.py 5day
if %errorlevel% neq 0 (
    echo ❌ 5일 예측 실패
    pause
    exit /b 1
)
echo.

echo [4/4] 10일 예측 생성 중...
py -3 scripts\predict_daily_multitf.py 10day
if %errorlevel% neq 0 (
    echo ❌ 10일 예측 실패
    pause
    exit /b 1
)
echo.

echo ========================================================================
echo ✅ 모든 타임프레임 예측 생성 완료!
echo ========================================================================
echo.
echo 생성된 파일:
dir /b predictions\today_predictions_*.json
echo.
pause

