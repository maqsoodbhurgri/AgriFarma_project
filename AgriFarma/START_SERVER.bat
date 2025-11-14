@echo off
color 0A
title AgriFarma Server

echo.
echo ========================================
echo   AGRIFARMA - Starting Server
echo ========================================
echo.

cd /d "%~dp0"

echo [1/3] Activating virtual environment...
call venv\Scripts\activate.bat

echo [2/3] Starting Flask server...
echo.
start /B python app.py

echo [3/3] Waiting for server to initialize...
timeout /t 4 /nobreak > nul

echo.
echo ========================================
echo   Server Started!
echo ========================================
echo.
echo   URL: http://127.0.0.1:5000
echo.
echo   Opening browser...
echo ========================================
echo.

start http://127.0.0.1:5000

echo.
echo ✓ Done! Check your browser.
echo.
echo To stop server: Close this window or press Ctrl+C
echo.
pause
