@echo off
cd /d "%~dp0"

python --version >nul 2>&1
if errorlevel 1 (
    echo Python not found. Install from https://python.org
    pause
    exit /b 1
)

pip install customtkinter mysql-connector-python reportlab --quiet --disable-pip-version-check

python main.py

if errorlevel 1 (
    echo.
    echo ERROR: Check that MySQL is running and password in database\db.py is correct.
    pause
)
