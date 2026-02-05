@echo off
REM ============================================================
REM Educational AI Platform - Stop Server
REM ============================================================

echo.
echo ========================================
echo   Stopping Educational AI Platform
echo ========================================
echo.

REM Kill Python processes running app.py
echo Stopping server...
taskkill /F /FI "WINDOWTITLE eq app.py*" >nul 2>&1
taskkill /F /FI "IMAGENAME eq python.exe" /FI "MEMUSAGE gt 50000" >nul 2>&1

echo.
echo Server stopped!
echo.
pause
