@echo off
REM Run script for Audio-Controlled Pong Game - Windows

REM Check if venv exists
if not exist venv (
    echo Virtual environment not found. Running setup...
    call setup.bat
    if %ERRORLEVEL% NEQ 0 exit /b 1
)

REM Activate venv and run
call venv\Scripts\activate.bat
python main.py
deactivate

