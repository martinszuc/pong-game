@echo off
REM Setup script for Audio-Controlled Pong Game - Windows
REM Requires Python 3.11

echo === Audio-Controlled Pong Game - Windows Setup ===
echo.

REM Find Python 3.11 (try multiple commands)
set PYTHON_CMD=

REM Try python-3.11 first
python-3.11 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python-3.11
    goto :found_python
)

REM Try py -3.11 (Windows launcher)
py -3.11 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py -3.11
    goto :found_python
)

REM Try python3.11
python3.11 --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python3.11
    goto :found_python
)

REM Try regular python (check if it's 3.10+)
python --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=python
    goto :found_python
)

REM Try py (Windows launcher)
py --version >nul 2>&1
if %ERRORLEVEL% EQU 0 (
    set PYTHON_CMD=py
    goto :found_python
)

echo ERROR: Python not found!
echo.
echo Please install Python 3.11 from:
echo https://www.python.org/downloads/
echo.
echo Make sure to check "Add Python to PATH" during installation!
pause
exit /b 1

:found_python
echo Found Python:
%PYTHON_CMD% --version
echo.

REM Remove old venv if it exists
if exist venv (
    echo Removing old virtual environment...
    rmdir /s /q venv
)

echo Creating virtual environment...
%PYTHON_CMD% -m venv venv

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

