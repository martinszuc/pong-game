#!/bin/bash
# Run script for Audio-Controlled Pong Game
# Supports: macOS, Linux

# check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    bash setup.sh
    if [ $? -ne 0 ]; then
        echo "Setup failed. Please fix errors above."
        exit 1
    fi
fi

# activate virtual environment
if [ -f "venv/bin/activate" ]; then
    # macOS/Linux
    source venv/bin/activate
    PYTHON_CMD="python"
elif [ -f "venv/Scripts/activate" ]; then
    # Windows (Git Bash)
    source venv/Scripts/activate
    PYTHON_CMD="python"
else
    echo "Error: Could not find virtual environment activation script"
    exit 1
fi

# verify venv uses Python 3.11
VENV_VERSION=$($PYTHON_CMD --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [ "$VENV_VERSION" != "3.11" ]; then
    echo "Warning: Virtual environment uses Python $VENV_VERSION instead of 3.11"
    echo "Re-running setup..."
    deactivate 2>/dev/null
    rm -rf venv
    bash setup.sh
    exit 0
fi

# run the game
echo "Starting Audio-Controlled Pong Game..."
$PYTHON_CMD main.py

# deactivate on exit
deactivate 2>/dev/null
