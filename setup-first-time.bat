@echo off
REM ============================================================
REM Educational AI Platform - First Time Setup with Virtual Environment
REM Run this ONCE before using start.bat
REM ============================================================

echo.
echo ========================================
echo   Educational AI Platform Setup
echo ========================================
echo.
echo This will install all requirements.
echo Estimated time: 10-20 minutes
echo.
pause

REM Change to script directory
cd /d "%~dp0"

REM ============================================================
REM Step 1: Check Python
REM ============================================================
echo.
echo [1/7] Checking Python installation...
python --version
if errorlevel 1 (
    echo.
    echo ERROR: Python is not installed!
    echo.
    echo Please install Python 3.10 or higher:
    echo 1. Visit: https://www.python.org/downloads/
    echo 2. Download Python 3.10+
    echo 3. During installation, CHECK "Add Python to PATH"
    echo 4. Run this script again
    echo.
    pause
    exit /b 1
)
echo     Python OK!

REM ============================================================
REM Step 2: Create Virtual Environment
REM ============================================================
echo.
echo [2/7] Creating virtual environment...
if exist "venv" (
    echo     Virtual environment already exists!
) else (
    python -m venv venv
    if errorlevel 1 (
        echo ERROR: Failed to create virtual environment
        pause
        exit /b 1
    )
    echo     Virtual environment created!
)

REM ============================================================
REM Step 3: Activate Virtual Environment
REM ============================================================
echo.
echo [3/7] Activating virtual environment...
call venv\Scripts\activate.bat
if errorlevel 1 (
    echo ERROR: Failed to activate virtual environment
    pause
    exit /b 1
)
echo     Virtual environment activated!

REM ============================================================
REM Step 4: Upgrade pip
REM ============================================================
echo.
echo [4/7] Upgrading pip...
python -m pip install --upgrade pip
echo     pip upgraded!

REM ============================================================
REM Step 5: Install Python dependencies
REM ============================================================
echo.
echo [5/7] Installing Python packages...
echo     This may take 5-10 minutes...
python -m pip install -r requirements.txt
if errorlevel 1 (
    echo ERROR: Failed to install Python packages
    pause
    exit /b 1
)
echo     Python packages installed!

REM ============================================================
REM Step 6: Create directories
REM ============================================================
echo.
echo [6/7] Creating directories...
if not exist "videos" mkdir videos
if not exist "temp" mkdir temp
echo     Directories created!

REM ============================================================
REM Step 7: Install Ollama and Model
REM ============================================================
echo.
echo [7/7] Setting up Ollama and AI model...

REM Check if Ollama is installed
where ollama >nul 2>&1
if errorlevel 1 (
    echo.
    echo Ollama is not installed.
    echo.
    echo Please install Ollama:
    echo 1. Visit: https://ollama.ai/download
    echo 2. Download Ollama for Windows
    echo 3. Install it
    echo 4. Run this script again
    echo.
    echo Press any key to open the download page...
    pause >nul
    start https://ollama.ai/download
    exit /b 1
) else (
    echo     Ollama is installed!
)

REM Check if Ollama is running
curl -s http://localhost:11434/api/tags >nul 2>&1
if errorlevel 1 (
    echo     Starting Ollama service...
    start /B ollama serve
    timeout /t 5 /nobreak >nul
)

echo.
echo Choose AI model to download:
echo 1. Mistral (7B) - Recommended, balanced performance
echo 2. LLaMA3 (8B) - Higher quality, slower
echo 3. Phi3 (3.8B) - Lightweight, faster
echo.
set /p choice="Enter choice (1-3): "

if "%choice%"=="1" set model=mistral
if "%choice%"=="2" set model=llama3
if "%choice%"=="3" set model=phi3
if "%choice%"=="" set model=mistral

echo.
echo Downloading %model% model...
echo This is a one-time download (~4-7GB)
echo This may take 10-20 minutes depending on your internet speed...
echo.
ollama pull %model%
if errorlevel 1 (
    echo ERROR: Failed to download model
    pause
    exit /b 1
)

REM ============================================================
REM Setup Complete
REM ============================================================
echo.
echo ========================================
echo   SETUP COMPLETE!
echo ========================================
echo.
echo Everything is ready to use!
echo.
echo To start the application:
echo   - Double-click: start.bat
echo   - Or run: start.bat
echo.
echo Then open: http://localhost:8000
echo.
pause
