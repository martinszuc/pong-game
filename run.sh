#!/bin/bash
# Run script for Audio-Controlled Pong Game
# Uses Python 3.11

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    bash setup.sh
fi

# Verify venv uses Python 3.11
VENV_PYTHON_VERSION=$(./venv/bin/python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
if [ "$VENV_PYTHON_VERSION" != "3.11" ]; then
    echo "Virtual environment uses Python $VENV_PYTHON_VERSION instead of 3.11."
    echo "Re-running setup to create correct environment..."
    rm -rf venv
    bash setup.sh
fi

source venv/bin/activate
python main.py
deactivate
