#!/bin/bash
# Setup script for Audio-Controlled Pong Game

echo "=== Setting up Python virtual environment ==="

if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed. Please install Python 3.8 or higher."
    exit 1
fi

if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
        echo "Installing audio libraries..."
        brew install flac libsndfile portaudio 2>/dev/null || true
    fi
fi

echo "Creating virtual environment..."
python3 -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=== Setup complete! ==="
echo "Run: ./run.sh"

