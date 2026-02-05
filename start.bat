@echo off
REM ============================================================
REM Educational AI Platform - One-Click Launcher with venv
REM ============================================================

echo.
echo ========================================
echo   Educational AI Platform Launcher
echo ========================================
echo.

REM Change to script directory
cd /d "%~dp0"

REM ============================================================
REM Step 1: Check if virtual environment exists
REM ============================================================
echo [1/6] Checking virtual environment...
if not exist "venv" (
    echo.
    echo ERROR: Virtual environment not found!
    echo Please run setup-first-time.bat first.
    echo.
    pause
    exit /b 1
)
echo     Virtual environment found!

REM ============================================================
REM Step 2: Activate virtual environment
REM ============================================================
echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo     Virtual environment activated!

REM ============================================================
REM Step 3: Check Python Installation
REM ============================================================
echo [3/6] Checking Python...
python --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Python is not available in virtual environment
    pause
    exit /b 1
)
echo     Python ready!

REM ============================================================
REM Step 4: Create directories if they don't exist
REM ============================================================
echo [4/6] Checking directories...
if not exist "videos" mkdir videos
if not exist "temp" mkdir temp
echo     Directories ready!

REM ============================================================
REM Step 5: Check Ollama and start if needed
REM ============================================================
echo [5/6] Checking Ollama service...

REM Check if Ollama is running
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo     Ollama is not running. Starting Ollama...
    
    REM Check if Ollama is installed
    where ollama >nul 2>&1
    if errorlevel 1 (
        echo.
        echo ========================================
        echo   OLLAMA NOT INSTALLED
        echo ========================================
        echo.
        echo Please install Ollama first:
        echo 1. Visit: https://ollama.ai/download
        echo 2. Download and install Ollama for Windows
        echo 3. Run this script again
        echo.
        pause
        exit /b 1
    )
    
    REM Start Ollama in background
    start /B ollama serve
    
    REM Wait for Ollama to start
    echo     Waiting for Ollama to start...
    timeout /t 5 /nobreak >nul
    
    REM Check if model exists
    echo     Checking for AI model...
    ollama list | findstr "mistral llama phi" >nul 2>&1
    if errorlevel 1 (
        echo.
        echo     No AI model found!
        echo     Downloading mistral model...
        echo     This may take 5-10 minutes...
        ollama pull mistral
        if errorlevel 1 (
            echo ERROR: Failed to download model
            pause
            exit /b 1
        )
    )
) else (
    echo     Ollama is already running!
)

REM ============================================================
REM Step 6: Start the application
REM ============================================================
echo [6/6] Starting Educational AI Platform...
echo.
echo ========================================
echo   SERVER STARTING
echo ========================================
echo.
echo The application will open in your browser.
echo Server URL: http://localhost:8000
echo.
echo Press Ctrl+C to stop the server
echo ========================================
echo.

REM Wait a moment
timeout /t 2 /nobreak >nul

REM Open browser after a short delay
start "" http://localhost:8000

REM Start the FastAPI server (using venv Python)
python app.py

REM If server stops
echo.
echo Server stopped.
pause
