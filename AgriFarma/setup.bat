@echo off
echo ========================================
echo AgriFarma - Automated Setup Script
echo ========================================
echo.

echo [1/6] Creating virtual environment...
python -m venv venv
if errorlevel 1 (
    echo Error: Failed to create virtual environment
    pause
    exit /b 1
)

echo [2/6] Activating virtual environment...
call venv\Scripts\activate.bat

echo [3/6] Installing dependencies...
pip install -r requirements.txt
if errorlevel 1 (
    echo Error: Failed to install dependencies
    pause
    exit /b 1
)

echo [4/6] Setting up environment file...
if not exist .env (
    copy .env.example .env
    echo Environment file created (.env)
) else (
    echo Environment file already exists
)

echo [5/6] Initializing database...
flask init-db

echo [6/6] Setup complete!
echo.
echo ========================================
echo Next Steps:
echo ========================================
echo 1. (Optional) Create admin user: flask create-admin
echo 2. Run the application: flask run
echo 3. Open browser: http://127.0.0.1:5000
echo.
echo To activate the virtual environment in future:
echo   venv\Scripts\activate
echo.
pause
