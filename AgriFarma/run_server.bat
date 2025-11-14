@echo off
echo ========================================
echo   AGRIFARMA - Starting Server
echo ========================================
echo.

cd /d "%~dp0"

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Starting Flask server...
echo.
echo ========================================
echo   Server URL: http://127.0.0.1:5000
echo ========================================
echo.
echo Press Ctrl+C to stop the server
echo.

python app.py

pause
