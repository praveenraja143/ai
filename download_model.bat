@echo off
REM Download Mistral AI Model for Ollama
echo.
echo ========================================
echo   Downloading Mistral AI Model
echo ========================================
echo.
echo This will download ~4GB of data
echo Estimated time: 5-15 minutes
echo.
pause

REM Use full path to ollama
"%LOCALAPPDATA%\Programs\Ollama\ollama.exe" pull mistral

if errorlevel 1 (
    echo.
    echo ERROR: Failed to download model
    echo.
    pause
    exit /b 1
)

echo.
echo ========================================
echo   Model Downloaded Successfully!
echo ========================================
echo.
echo Now run: python test_ollama.py
echo.
pause
