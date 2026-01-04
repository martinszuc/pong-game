#!/bin/bash
    # Universal setup script for Audio-Controlled Pong Game
# Supports: macOS, Linux (Fedora/Ubuntu/Debian), Windows (Git Bash)
# Requires: Python 3.11

echo "=== Audio-Controlled Pong Game - Setup ==="
echo ""

# detect operating system
OS="unknown"
if [[ "$OSTYPE" == "darwin"* ]]; then
    OS="macos"
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    OS="linux"
elif [[ "$OSTYPE" == "msys" || "$OSTYPE" == "cygwin" ]]; then
    OS="windows"
fi

echo "Detected OS: $OS"
echo ""

# install system dependencies based on OS
if [ "$OS" == "linux" ]; then
    echo "=== Installing Linux system dependencies ==="
    
    # detect Linux distro
    if [ -f /etc/fedora-release ]; then
        echo "Detected: Fedora/RHEL"
        echo "Installing build tools and libraries..."
        sudo dnf install -y gcc gcc-c++ make \
            python3.11-devel \
            gtk3-devel \
            portaudio-devel libsndfile-devel flac-devel \
            SDL2-devel \
            libjpeg-turbo-devel libpng-devel libtiff-devel \
            webkit2gtk4.0-devel libnotify-devel freeglut-devel || {
            echo "Warning: Some packages may have failed to install"
            echo "You may need to install them manually"
        }
    elif [ -f /etc/debian_version ]; then
        echo "Detected: Debian/Ubuntu"
        echo "Installing build tools and libraries..."
        sudo apt-get update
        sudo apt-get install -y build-essential \
            python3.11-dev \
            libgtk-3-dev \
            portaudio19-dev libsndfile1-dev libflac-dev \
            libsdl2-dev \
            libjpeg-dev libpng-dev libtiff-dev \
            libwebkit2gtk-4.0-dev libnotify-dev freeglut3-dev || {
            echo "Warning: Some packages may have failed to install"
            echo "You may need to install them manually"
        }
    else
        echo "Warning: Unknown Linux distribution"
        echo "Please install these manually:"
        echo "  - gcc, g++, make (build tools)"
        echo "  - python3.11-dev"
        echo "  - gtk3-dev, portaudio-dev, libsndfile-dev"
        read -p "Press Enter to continue anyway..."
    fi
    echo ""
    
elif [ "$OS" == "macos" ]; then
    echo "=== Installing macOS dependencies via Homebrew ==="
    
    if ! command -v brew &> /dev/null; then
        echo "Warning: Homebrew is not installed."
        echo "Install it from: https://brew.sh"
        echo "Or run: /bin/bash -c \"\$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)\""
        read -p "Press Enter to continue anyway..."
    else
        echo "Installing audio libraries..."
        brew install flac libsndfile portaudio 2>/dev/null || true
    fi
    echo ""
fi

# find Python 3.11
echo "=== Finding Python 3.11 ==="
PYTHON_CMD=""

if command -v python3.11 &> /dev/null; then
    PYTHON_CMD="python3.11"
elif command -v python3 &> /dev/null; then
    # check if python3 is actually 3.11
    VERSION=$(python3 --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    if [ "$VERSION" == "3.11" ]; then
        PYTHON_CMD="python3"
    fi
elif command -v python &> /dev/null; then
    # check if python is 3.11
    VERSION=$(python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
    if [ "$VERSION" == "3.11" ]; then
        PYTHON_CMD="python"
    fi
fi

if [ -z "$PYTHON_CMD" ]; then
    echo "Error: Python 3.11 not found!"
    echo ""
    echo "Please install Python 3.11:"
    echo "  - macOS: brew install python@3.11"
    echo "  - Fedora: sudo dnf install python3.11"
    echo "  - Ubuntu: sudo apt install python3.11"
    echo "  - Windows: Download from python.org"
    exit 1
fi

echo "Using: $PYTHON_CMD"
$PYTHON_CMD --version
echo ""

# remove old venv if it exists with wrong Python version
if [ -d "venv" ]; then
    if [ -f "venv/bin/python" ]; then
        VENV_PYTHON_VERSION=$(./venv/bin/python --version 2>&1 | grep -oE '[0-9]+\.[0-9]+')
        if [ "$VENV_PYTHON_VERSION" != "3.11" ]; then
            echo "Existing venv uses Python $VENV_PYTHON_VERSION, removing..."
            rm -rf venv
        fi
    fi
fi

echo "=== Creating virtual environment ==="
$PYTHON_CMD -m venv venv

echo "Activating virtual environment..."
if [ -f "venv/bin/activate" ]; then
    source venv/bin/activate
elif [ -f "venv/Scripts/activate" ]; then
    source venv/Scripts/activate
else
    echo "Error: Could not find venv activation script"
    exit 1
fi

echo ""
echo "=== Installing Python packages ==="
echo "Upgrading pip..."
pip install --upgrade pip

echo ""
echo "Installing dependencies..."
echo "Note: On Linux, wxPython compilation takes 10-20 minutes..."
pip install -r requirements.txt

if [ $? -ne 0 ]; then
    echo ""
    echo "❌ Installation failed!"
    echo ""
    if [ "$OS" == "linux" ]; then
        echo "On Linux, you need system development libraries installed."
        echo "Run this setup script again - it will attempt to install them."
        echo ""
        echo "If it still fails, install manually:"
        echo "  Fedora: sudo dnf install gcc gcc-c++ python3.11-devel gtk3-devel portaudio-devel"
        echo "  Ubuntu: sudo apt install build-essential python3.11-dev libgtk-3-dev portaudio19-dev"
    fi
    exit 1
fi

echo ""
echo "✅ Setup complete!"
echo ""
echo "Run the game:"
echo "  ./run.sh"
echo ""
