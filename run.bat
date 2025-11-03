@echo off
REM Run script for Audio-Controlled Pong Game (Windows)

REM Check if virtual environment exists
if not exist "venv" (
    echo Virtual environment not found. Running setup...
    call setup.bat
)

REM Activate virtual environment
call venv\Scripts\activate.bat

REM Run the game
python main.py

REM Deactivate when done
deactivate

pause

