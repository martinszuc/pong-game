# Audio-Controlled Pong Game

A Pong game controlled by microphone input. The paddle falls down by default and noise/voice raises it up. Score is based on number of bounces (paddle hits).

## Setup

1. Install Python 3.8 or higher
2. Create virtual environment:
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```
3. Install dependencies:
   ```bash
   pip install --upgrade pip
   pip install -r requirements.txt
   ```

## Run

```bash
./run.sh
```

Or manually:
```bash
source venv/bin/activate
python main.py
```

## Controls

- W/S: Move left paddle (keyboard override)
- Microphone/Noise: Left paddle control (paddle falls down, noise raises it up)
- Arrow Keys: Move right paddle (if AI disabled)
- SPACE: Pause/Resume
- ESC: Return to Menu
- R: Reset Game

