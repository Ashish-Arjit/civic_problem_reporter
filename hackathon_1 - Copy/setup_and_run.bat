@echo off
setlocal
echo ==========================================
echo       CivicFix Backend Master Setup
echo ==========================================

echo [1/3] Installing/Updating dependencies...
pip install -r requirements.txt
if %ERRORLEVEL% NEQ 0 (
    echo Error installing dependencies. Make sure Python/pip are installed.
    pause
    exit /b
)

echo [2/3] Starting Flask Server in a new window...
:: This starts the server in a separate window so the current script can continue
start "CivicFix Backend Server" cmd /k python app.py

echo Waiting for server to initialize...
timeout /t 5 /nobreak > nul

echo [3/3] Running Demo Tests...
call demo_test.bat

echo ==========================================
echo Project is running! 
echo Keep the server window open for the demo.
echo ==========================================
pause
