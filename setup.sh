#!/bin/bash
# Setup script for Audio-Controlled Pong Game
# Requires Python 3.11

echo "=== Setting up Python virtual environment ==="

# Determine Python 3.11 command
PYTHON_CMD=""

# Check for python3.11 first
if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
# On macOS, check Homebrew Python 3.11
elif [[ "$OSTYPE" == "darwin"* ]]; then
    # Check if Homebrew is installed
    if ! command -v brew &> /dev/null; then
        echo "Error: Homebrew is not installed."
        echo "Install Homebrew first: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        exit 1
    fi
    
    echo "Python 3.11 not found. Installing via Homebrew..."
    brew install python@3.11
    
    # After installation, find the python command
    if command -v python3.11 &> /dev/null; then
        PYTHON_CMD="python3.11"
    elif [ -x "/opt/homebrew/bin/python3.11" ]; then
        PYTHON_CMD="/opt/homebrew/bin/python3.11"
    elif [ -x "/usr/local/bin/python3.11" ]; then
        PYTHON_CMD="/usr/local/bin/python3.11"
    else
        # Try to get path from brew
        BREW_PREFIX=$(brew --prefix python@3.11 2>/dev/null)
        if [ -n "$BREW_PREFIX" ] && [ -x "$BREW_PREFIX/bin/python3.11" ]; then
            PYTHON_CMD="$BREW_PREFIX/bin/python3.11"
        fi
    fi
else
    echo "Error: Python 3.11 is not installed."
    echo "Please install Python 3.11 for your system."
    exit 1
fi

# Final check
if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Could not find Python 3.11 after installation attempt."
    echo "Please ensure Python 3.11 is installed and in your PATH."
    exit 1
fi

echo "Using Python: $PYTHON_CMD"
$PYTHON_CMD --version

# macOS: Install required audio libraries
if [[ "$OSTYPE" == "darwin"* ]]; then
    if command -v brew &> /dev/null; then
        echo "Installing audio libraries via Homebrew..."
        brew install flac libsndfile portaudio 2>/dev/null || true
    fi
fi

# Remove old venv if it exists with wrong Python version
if [ -d "venv" ]; then
    VENV_PYTHON_VERSION=$(./venv/bin/python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    if [ "$VENV_PYTHON_VERSION" != "3.11" ]; then
        echo "Existing venv uses Python $VENV_PYTHON_VERSION, removing to recreate with 3.11..."
        rm -rf venv
    fi
fi

echo "Creating virtual environment with Python 3.11..."
$PYTHON_CMD -m venv venv

echo "Activating virtual environment..."
source venv/bin/activate

echo "Upgrading pip..."
pip install --upgrade pip

echo "Installing dependencies..."
pip install -r requirements.txt

echo ""
echo "=== Setup complete! ==="
echo "Run: ./run.sh"
