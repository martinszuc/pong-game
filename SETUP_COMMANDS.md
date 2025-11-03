# Setup and Run Commands

## Quick Start (macOS/Linux)

```bash
# First time setup - creates virtual environment and installs dependencies
bash setup.sh

# Run the game
bash run.sh
```

## Quick Start (Windows)

```cmd
REM First time setup
setup.bat

REM Run the game
run.bat
```

## Manual Setup (Step by Step)

### 1. Check Python Installation
```bash
# macOS/Linux
python3 --version

# Windows
python --version
```
Should show Python 3.8 or higher.

### 2. Create Virtual Environment
```bash
# macOS/Linux
python3 -m venv venv

# Windows
python -m venv venv
```

### 3. Activate Virtual Environment
```bash
# macOS/Linux
source venv/bin/activate

# Windows
venv\Scripts\activate.bat
```

When activated, your prompt will show `(venv)`.

### 4. Install Dependencies
```bash
pip install --upgrade pip
pip install -r requirements.txt
```

**Note for macOS users:** If `pyo` installation fails, install portaudio first:
```bash
brew install portaudio
```

**Note for Linux users:** Install system dependencies first:
```bash
sudo apt-get install portaudio19-dev python3-dev
```

### 5. Run the Game
```bash
python main.py
```

### 6. Deactivate Virtual Environment (when done)
```bash
deactivate
```

## Troubleshooting

### Virtual environment already exists?
Just activate it and run:
```bash
source venv/bin/activate  # macOS/Linux
# or
venv\Scripts\activate.bat  # Windows

python main.py
```

### Need to reinstall dependencies?
```bash
source venv/bin/activate  # or activate on Windows
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Remove and recreate virtual environment?
```bash
rm -rf venv  # macOS/Linux
# or
rmdir /s venv  # Windows

# Then run setup.sh or setup.bat again
```

