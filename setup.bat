@echo off
REM Setup script for Audio-Controlled Pong Game (Windows)

echo === Setting up Python virtual environment ===

REM Check if Python is installed
python --version >nul 2>&1
if errorlevel 1 (
    echo Error: Python is not installed or not in PATH.
    echo Please install Python 3.8 or higher from https://www.python.org/
    pause
    exit /b 1
)

REM Create virtual environment
echo Creating virtual environment...
python -m venv venv

REM Activate virtual environment
echo Activating virtual environment...
call venv\Scripts\activate.bat

REM Upgrade pip
echo Upgrading pip...
python -m pip install --upgrade pip

REM Install dependencies
echo Installing dependencies...
pip install -r requirements.txt

echo.
echo === Setup complete! ===
echo.
echo To activate the virtual environment, run:
echo   venv\Scripts\activate.bat
echo.
echo To run the game, use:
echo   python main.py
echo.
pause

