@echo off
REM ============================================================
REM Quick Fix Script for Educational AI Platform
REM Run this to automatically fix common issues
REM ============================================================

echo.
echo ========================================
echo   Educational AI Platform - Quick Fix
echo ========================================
echo.

cd /d "%~dp0"

REM Create missing directories
echo [1/5] Creating directories...
if not exist "videos" mkdir videos
if not exist "temp" mkdir temp
echo     Done!

REM Check for llm_engine.py
echo.
echo [2/5] Checking for missing files...
if not exist "llm_engine.py" (
    echo     WARNING: llm_engine.py is missing!
    echo     Please copy llm_engine.py to this folder.
    pause
    exit /b 1
)
echo     All files present!

REM Install/Update Python packages
echo.
echo [3/5] Installing Python packages...
python -m pip install --upgrade pip --quiet
python -m pip install -r requirements.txt --quiet
if errorlevel 1 (
    echo     ERROR: Failed to install packages
    echo     Try manually: pip install -r requirements.txt
    pause
    exit /b 1
)
echo     Packages installed!

REM Check Ollama
echo.
echo [4/5] Checking Ollama...
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo     Ollama is not running. Starting...
    where ollama >nul 2>&1
    if errorlevel 1 (
        echo.
        echo     ERROR: Ollama not installed!
        echo     Install from: https://ollama.ai/download
        pause
        exit /b 1
    )
    start /B ollama serve
    timeout /t 5 /nobreak >nul
)
echo     Ollama is running!

REM Check for Mistral model
echo.
echo [5/5] Checking AI model...
ollama list | findstr "mistral" >nul 2>&1
if errorlevel 1 (
    echo     Mistral model not found. Downloading...
    echo     This will take 5-15 minutes...
    ollama pull mistral
    if errorlevel 1 (
        echo     ERROR: Failed to download model
        pause
        exit /b 1
    )
)
echo     Model ready!

REM Run diagnostic
echo.
echo ========================================
echo   Running Full Diagnostic...
echo ========================================
python diagnose.py

echo.
echo ========================================
echo   Fix Complete!
echo ========================================
echo.
echo To start the application:
echo   1. Run: start.bat
echo   2. Or: python app.py
echo.
pause
