#!/bin/bash
# Run script for Audio-Controlled Pong Game

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "Virtual environment not found. Running setup..."
    bash setup.sh
fi

# Activate virtual environment
source venv/bin/activate

# Run the game
python main.py

# Deactivate when done
deactivate

