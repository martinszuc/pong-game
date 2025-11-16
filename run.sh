#!/bin/bash
# Run script for Audio-Controlled Pong Game

if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    bash setup.sh
fi

source venv/bin/activate
python main.py
deactivate

