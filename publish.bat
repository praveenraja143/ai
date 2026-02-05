@echo off
echo ===================================================
echo   EDUCATIONAL AI PLATFORM - PUBLIC PUBLISHING
echo ===================================================
echo.
echo 1. Starting Backend Server...
start "AI Backend Server" cmd /k "call .venv\Scripts\activate && uvicorn app:app --host 0.0.0.0 --port 8000"

echo.
echo 2. Waiting for server to initialize...
timeout /t 5 /nobreak >nul

echo.
echo 3. Starting Ngrok Tunnel...
echo.
echo IMPORTANT:
echo If this is your first time, you might need to add your auth token.
echo Sign up at: https://dashboard.ngrok.com/signup
echo Run command: ngrok config add-authtoken <YOUR_TOKEN>
echo.
echo Launching tunnel...
ngrok http 8000
pause
