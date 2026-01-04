@echo off
REM Setup script for Audio-Controlled Pong Game - Windows
REM Requires Python 3.11

echo === Audio-Controlled Pong Game - Windows Setup ===
echo.

REM Check for Python 3.11
python --version 2>nul | findstr /C:"3.11" >nul
if %ERRORLEVEL% NEQ 0 (
    echo ERROR: Python 3.11 not found!
    echo.
    echo Please install Python 3.11 from:
    echo https://www.python.org/downloads/
    echo.
    echo Make sure to check "Add Python to PATH" during installation!
    pause
    exit /b 1
)

echo Found Python 3.11
python --version
echo.

REM Remove old venv if it exists
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

echo Creating virtual environment...
python -m venv venv

echo Activating virtual environment...
call venv\Scripts\activate.bat

echo.
echo Upgrading pip...
python -m pip install --upgrade pip

echo.
echo Installing dependencies...
echo Note: This may take 5-10 minutes...
pip install -r requirements.txt

if %ERRORLEVEL% NEQ 0 (
    echo.
    echo ERROR: Installation failed!
    echo Check the error messages above.
    pause
    exit /b 1
)

echo.
echo ==============================
echo Setup complete!
echo ==============================
echo.
echo Run the game:
echo   run.bat
echo.
pause

