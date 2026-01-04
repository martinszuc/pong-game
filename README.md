# Audio-Controlled Pong Game

A Pong game controlled by microphone input. Paddle falls by default, noise raises it up. Score based on paddle bounces.

## Setup

**Linux - Install system dependencies first:**
```bash
# Fedora/RHEL
sudo dnf install gcc gcc-c++ python3.11-devel gtk3-devel portaudio-devel libsndfile-devel

# Ubuntu/Debian
sudo apt install build-essential python3.11-dev libgtk-3-dev portaudio19-dev libsndfile1-dev
```

**All platforms:**
```bash
./setup.sh    # One-time setup (Linux: takes 10-20 min for wxPython)
./run.sh      # Run the game
```

**Linux VM users:** Need at least 4GB free disk space for wxPython compilation

## Controls

- **Microphone/Noise**: Left paddle control (paddle falls down, noise raises it up)
- **SPACE**: Pause/Resume
- **ESC**: Return to Menu

## Code Structure

The code is organized into logical modules to make it easier to understand and maintain:

### Core Files
- **`main.py`** - The entry point. Starts the game and runs the main loop (60 times per second).

### Game Logic (`game/`)
- **`engine.py`** - The "brain" of the game. Handles physics, collisions, scoring, and game states.
- **`entities.py`** - Defines the game objects (Ball and Paddle). Each knows how to move and update itself.
- **`ai.py`** - The AI opponent that controls the right paddle. Purposely imperfect to keep the game fair!

### Audio Input (`audio/`)
- **`input_processor.py`** - Listens to your microphone and converts sound into paddle movement:
  - LOUD = paddle moves UP
  - QUIET/silence = paddle moves DOWN

### Visuals (`visuals/`)
- **`renderer.py`** - Draws everything on screen (paddles, ball, score, effects).
- **`effects.py`** - Handles visual effects (screen flashes, particles, etc.).

### User Interface (`ui/`)
- **`frame.py`** - The main game window and menu system.
- **`settings_dialog.py`** - Settings window (adjust microphone sensitivity).
- **`game_over_dialog.py`** - Game over screen and high score entry.

### Utilities (`utils/`)
- **`settings.py`** - Saves and loads game settings (like microphone sensitivity) to a JSON file.
- **`high_scores.py`** - Manages the high score leaderboard (top 5 scores).
- **`logger.py`** - Sets up logging so we can track what happens in the game.

### Lighting (Optional) (`lighting/`)
- **`artnet_controller.py`** - Controls DMX stage lights via Art-Net protocol (optional feature).

### How It All Works Together

1. **`main.py`** starts everything and creates the main game loop
2. The **game loop** runs 60 times per second and:
   - Reads the microphone (via `audio/input_processor.py`)
   - Updates game physics (via `game/engine.py`)
   - Draws everything (via `visuals/renderer.py`)
   - Updates the window (via `ui/frame.py`)
3. When the ball hits something, the **engine** triggers callbacks for:
   - Sound effects (not implemented in this version)
   - Visual effects (screen flashes, particles)
   - Lighting effects (if DMX lights are connected)

## Controls

- **Audio Mode**: Loud = paddle up, quiet = paddle down
- **Keyboard Mode**: W/S or Arrow keys
- **SPACE**: Pause/Resume
- **ESC**: Return to Menu

## Features

🎤 Microphone or keyboard control • 🎨 3 themes • 🎮 3 difficulties • 🎯 Auto-calibration • 📊 Audio viz • 💡 DMX lighting • 🏆 Leaderboard

## Troubleshooting

**Linux: "No space left on device"** - Need 4GB free for wxPython compilation. Free up space and re-run.

**"No module named 'wx'"** - Install system dependencies first (see Setup above), then `./setup.sh`

**Audio not working** - Run Settings → Calibration Wizard, or switch to Keyboard mode
