# Pong Game - Complete Codebase Reference
**For Team Use - AI Assistant Context Document**

> **Purpose**: This document contains the complete codebase for easy sharing with AI assistants (ChatGPT, Claude, etc.). Copy relevant sections when asking for help.

---

## 📋 Project Overview

**What it is**: Audio-controlled pong game where you use your microphone to control the left paddle.

**Tech Stack**:
- Python 3.11
- wxPython (GUI)
- OpenCV (graphics/rendering)
- pyo (audio processing)
- numpy (numerical operations)

**Game Mechanics**:
- Left paddle: controlled by microphone (loud = up, quiet = down) OR keyboard (W/S or arrows)
- Right paddle: AI opponent
- Score: number of paddle bounces before game over
- High scores saved to JSON file

**Features**:
- 🎨 3 Color Themes (Classic, Red Fire, Ocean Blue)
- 🎮 3 Difficulty Levels (Easy, Medium, Hard)
- 🎤 Audio Calibration Wizard
- 📊 Real-time Audio Visualization
- ⌨️ Keyboard Control Option (WASD + Arrow Keys)

---

## 🏗️ Project Architecture

```
pong-game/
├── main.py                    # Entry point, game loop
├── game/
│   ├── engine.py             # Game logic, physics, collisions
│   ├── entities.py           # Ball and Paddle classes
│   └── ai.py                 # AI opponent logic
├── audio/
│   └── input_processor.py    # Microphone input handling
├── visuals/
│   ├── renderer.py           # Drawing/rendering
│   └── effects.py            # Visual effects (flashes, particles)
├── ui/
│   ├── frame.py              # Main window and menu
│   ├── settings_dialog.py    # Settings window
│   └── game_over_dialog.py   # Game over screen
├── utils/
│   ├── settings.py           # Settings persistence
│   ├── high_scores.py        # High score management
│   └── logger.py             # Logging setup
└── lighting/
    └── artnet_controller.py  # DMX lighting (optional)
```

---

## 🎨 NEW: Color Themes System (`visuals/themes.py`)

**Purpose**: Define color schemes for the entire game.

```python
"""
themes.py - Color themes for the game
"""

THEMES = {
    'classic': {
        'name': 'Classic',
        'paddle': (255, 255, 255),      # white (BGR)
        'ball': (255, 255, 0),          # cyan/yellow (BGR)
        'center_line': (128, 128, 128), # gray (BGR)
        'score': (0, 0, 255),           # red (BGR)
        'bg_tint': (0, 0, 0),           # black (BGR)
        'menu_bg': (30, 30, 30),        # dark gray (RGB)
        'menu_title': (255, 255, 255),  # white (RGB)
    },
    'red': {
        'name': 'Red Fire',
        'paddle': (0, 0, 255),          # red (BGR)
        'ball': (100, 100, 255),        # pink (BGR)
        'menu_bg': (25, 0, 0),          # dark red (RGB)
        'menu_title': (255, 100, 100),  # pink (RGB)
    },
    'blue': {
        'name': 'Ocean Blue',
        'paddle': (255, 150, 0),        # blue (BGR)
        'ball': (255, 255, 150),        # cyan (BGR)
        'menu_bg': (0, 15, 35),         # dark blue (RGB)
        'menu_title': (150, 220, 255),  # cyan (RGB)
    }
}

def get_theme(theme_name):
    return THEMES.get(theme_name, THEMES['classic'])
```

**Key Points**:
- Game colors in BGR (for OpenCV)
- Menu colors in RGB (for wxPython)
- Themes affect entire UI (game + menu)

---

## 🎮 NEW: Difficulty Presets

**In `game/engine.py`:**

```python
DIFFICULTY_PRESETS = {
    'easy': {
        'ai_difficulty': 0.4,
        'ball_speed': 200,
        'paddle_speed': 350,
        'speed_increase': 1.03,
        'max_speed_mult': 2.0
    },
    'medium': {
        'ai_difficulty': 0.6,
        'ball_speed': 250,
        'paddle_speed': 300,
        'speed_increase': 1.05,
        'max_speed_mult': 2.5
    },
    'hard': {
        'ai_difficulty': 0.85,
        'ball_speed': 320,
        'paddle_speed': 270,
        'speed_increase': 1.08,
        'max_speed_mult': 3.0
    }
}
```

---

## 🔧 Core Components

### 1. Main Entry Point (`main.py`)

**Purpose**: Initializes everything and runs the game loop (60 FPS).

```python
"""
main.py - The entry point of the audio-controlled pong game

This file starts the entire game application. It sets up all the necessary 
components (audio, graphics, game logic) and runs the main game loop.
"""

import wx
import time
import sys
import logging
import platform

from game.engine import PongGame
from visuals.renderer import Renderer
from ui.frame import PongFrame
from utils.logger import setup_logging, get_logger
from pyo import Server

# Game configuration
FIELD_WIDTH = 800
FIELD_HEIGHT = 600
TIMER_INTERVAL_MS = 16  # ~60 FPS
MAX_DELTA_TIME = 0.1

setup_logging()
logger = get_logger(__name__)


class PongApplication:
    """Main application class - sets up and runs the entire pong game"""
    
    def __init__(self):
        self.field_width = FIELD_WIDTH
        self.field_height = FIELD_HEIGHT
        
        # Initialize all components
        self._init_wx_app()      # Window system
        self._init_audio()       # Microphone
        self._init_lighting()    # DMX lights (optional)
        self._init_game()        # Game engine
        self._init_ui()          # Window
        self._init_timer()       # Game loop timer
    
    def _init_audio(self):
        """Set up audio system for microphone input"""
        try:
            self.audio_server = Server().boot()
            self.audio_server.start()
        except Exception as e:
            logger.error(f"Failed to start audio server: {e}")
            self.audio_server = None
        
        from audio.input_processor import AudioInputProcessor
        from utils.settings import SettingsManager
        
        self.settings = SettingsManager()
        audio_sensitivity = self.settings.get_audio_sensitivity()
        self.audio_input = AudioInputProcessor(
            server=self.audio_server, 
            noise_threshold=audio_sensitivity
        )
        
        if self.audio_server is not None:
            self.audio_input.start(self.audio_server)
    
    def on_timer(self, event):
        """Main game loop - runs 60 times per second"""
        if not self.running:
            return
        
        try:
            # Calculate delta time
            current_time = time.time()
            delta_time = min(current_time - self.last_time, MAX_DELTA_TIME)
            self.last_time = current_time
            
            # Handle paddle input
            if self.game.game_state == 'playing' and self.audio_input:
                paddle_dir = self.audio_input.get_paddle_direction()
                if paddle_dir == -1:  # Loud
                    self.game.paddle_left.move_up()
                elif paddle_dir == 1:  # Quiet
                    self.game.paddle_left.move_down()
            
            # Update game state
            self.renderer.update_effects(delta_time)
            self.game.update(delta_time)
            
            # Render frame
            frame = self.renderer.render(self.game)
            self.frame.update_display(frame)
            
        except Exception as e:
            logger.error(f"Error in game loop: {e}", exc_info=True)
```

**Key Points**:
- Game loop runs every 16ms (60 FPS)
- Reads microphone → updates physics → renders → displays
- Delta time keeps game speed consistent

---

### 2. Game Engine (`game/engine.py`)

**Purpose**: Handles all game logic - physics, collisions, scoring.

```python
"""
engine.py - The game engine (the "brain" of the game)
"""

import logging
import random
from .entities import Ball, Paddle

# Configuration constants
PADDLE_WIDTH = 10
PADDLE_HEIGHT = 80
PADDLE_SPEED = 300
PADDLE_MARGIN = 20
BALL_RADIUS = 8
BALL_SPEED = 250
BALL_ANGLE_RANGE = (-0.5, 0.5)
PADDLE_HIT_VELOCITY_BOOST = 50
AI_DIFFICULTY = 0.6


class PongGame:
    """Main game engine - manages physics, collisions, scoring"""
    
    def __init__(self, field_width, field_height):
        self.field_width = field_width
        self.field_height = field_height
        self.score_left = 0
        self.score_right = 0
        self.game_state = 'menu'  # 'menu', 'playing', 'paused', 'game_over'
        self.bounce_count = 0
        
        self._init_paddles()
        self._init_ai()
        self.reset_ball()
    
    def update(self, delta_time):
        """Update game for one frame"""
        if self.game_state != 'playing':
            return
        
        # Update AI
        if self.ai:
            self.ai.update(self.ball, delta_time)
        
        # Move paddles and ball
        self.paddle_left.update(delta_time, self.field_height)
        self.paddle_right.update(delta_time, self.field_height)
        self.ball.update(delta_time)
        
        # Check collisions
        self._handle_wall_collisions()
        self._handle_paddle_collisions()
        self._handle_goals()
        self._normalize_ball_velocity()
    
    def check_collision(self, ball, paddle):
        """Check if ball and paddle are touching (AABB collision)"""
        ball_left, ball_top, ball_right, ball_bottom = ball.get_rect()
        paddle_left, paddle_top, paddle_right, paddle_bottom = paddle.get_rect()
        
        return (ball_right >= paddle_left and 
                ball_left <= paddle_right and
                ball_bottom >= paddle_top and
                ball_top <= paddle_bottom)
    
    def _handle_paddle_hit(self, paddle, side):
        """Bounce ball off paddle and apply spin"""
        # Move ball away from paddle
        if side == 'left':
            self.ball.position[0] = paddle.position[0] + paddle.width + self.ball.radius
        else:
            self.ball.position[0] = paddle.position[0] - self.ball.radius
        
        # Bounce and speed up
        self.ball.reflect_x()
        self.ball.increase_speed()
        
        # Apply spin based on hit position
        hit_position = self._calculate_hit_position(paddle)
        self.ball.velocity[1] += hit_position * PADDLE_HIT_VELOCITY_BOOST
    
    def _handle_goals(self):
        """Check if someone scored"""
        ball_x = self.ball.position[0]
        
        if ball_x < 0:  # Player missed
            self.game_state = 'game_over'
        elif ball_x > self.field_width:  # AI missed
            self.game_state = 'game_over'
```

**Key Points**:
- Collision detection uses AABB (axis-aligned bounding boxes)
- Ball speeds up after each paddle hit (capped at 2.5x)
- Spin is applied based on where ball hits paddle
- Game over when ball goes off either side

---

### 3. Game Entities (`game/entities.py`)

**Purpose**: Defines Ball and Paddle objects.

```python
"""
entities.py - Game objects (ball and paddles)
"""

DEFAULT_SPEED_INCREASE_FACTOR = 1.05  # 5% faster per hit
DEFAULT_MAX_SPEED_MULTIPLIER = 2.5    # Max 2.5x starting speed


class Ball:
    """The pong ball"""
    
    def __init__(self, x, y, radius, velocity_x, velocity_y):
        self.position = [float(x), float(y)]
        self.radius = radius
        self.velocity = [float(velocity_x), float(velocity_y)]
        self.base_speed = (velocity_x**2 + velocity_y**2)**0.5
        self.speed = self.base_speed
        self.max_speed = self.base_speed * DEFAULT_MAX_SPEED_MULTIPLIER
    
    def update(self, delta_time):
        """Move the ball"""
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time
    
    def reflect_x(self):
        """Bounce horizontally"""
        self.velocity[0] = -self.velocity[0]
    
    def reflect_y(self):
        """Bounce vertically"""
        self.velocity[1] = -self.velocity[1]
    
    def increase_speed(self):
        """Speed up (after paddle hit)"""
        self.speed = min(self.speed * 1.05, self.max_speed)


class Paddle:
    """A pong paddle"""
    
    def __init__(self, x, y, width, height, speed):
        self.position = [float(x), float(y)]
        self.width = width
        self.height = height
        self.speed = speed
        self.direction = 0  # -1=up, 0=stopped, 1=down
    
    def update(self, delta_time, field_height):
        """Move paddle and keep within bounds"""
        self.position[1] += self.direction * self.speed * delta_time
        
        # Clamp to field
        min_y = 0
        max_y = field_height - self.height
        self.position[1] = max(min_y, min(max_y, self.position[1]))
    
    def move_up(self):
        self.direction = -1
    
    def move_down(self):
        self.direction = 1
    
    def stop(self):
        self.direction = 0
```

**Key Points**:
- Simple physics: position += velocity * time
- Paddles clamped to screen boundaries
- Ball speed increases by 5% per hit (max 2.5x)

---

### 4. Audio Input (`audio/input_processor.py`)

**Purpose**: Converts microphone input to paddle movement.

```python
"""
input_processor.py - Audio input processing

Listens to microphone and converts sound into paddle movement:
- LOUD = paddle moves UP
- QUIET = paddle moves DOWN
"""

from pyo import Server, Input, Yin, RMS

DEFAULT_NOISE_THRESHOLD = 0.02
RMS_MULTIPLIER = 10


class AudioInputProcessor:
    """Processes microphone input to control the paddle"""
    
    def __init__(self, server=None, noise_threshold=DEFAULT_NOISE_THRESHOLD):
        self.server = server
        self.noise_threshold = noise_threshold
        self.audio_input = None
        self.volume_rms = None
        self.current_volume = 0.0
    
    def start(self, server=None):
        """Start listening to the microphone"""
        if server:
            self.server = server
        
        try:
            self.audio_input = Input(chnl=0)  # Default mic
            self.volume_rms = RMS(self.audio_input)  # Volume measurement
            return True
        except Exception as e:
            return False
    
    def get_paddle_direction(self):
        """
        Main control function:
        - If LOUD (volume > threshold) → return -1 (move UP)
        - If quiet (volume <= threshold) → return 1 (move DOWN)
        """
        volume = self.get_volume()
        return -1 if volume > self.noise_threshold else 1
    
    def get_volume(self):
        """Measure current microphone volume (0.0 to 1.0)"""
        if self.audio_input is None:
            return 0.0
        
        try:
            if self.volume_rms is not None:
                rms_value = self.volume_rms.get()
                volume = min(1.0, max(0.0, rms_value * RMS_MULTIPLIER))
            else:
                volume = abs(self.audio_input.get())
            
            self.current_volume = volume
        except Exception as e:
            self.current_volume = 0.0
        
        return self.current_volume
```

**Key Points**:
- Uses RMS (Root Mean Square) to measure volume
- Simple threshold-based control
- Adjustable sensitivity via settings

---

### 5. AI Opponent (`game/ai.py`)

**Purpose**: Controls the right paddle (computer opponent).

```python
"""
ai.py - Computer opponent AI
"""

AI_DIFFICULTY = 0.6  # 0.0 = easiest, 1.0 = hardest
AI_THRESHOLD = 15.0  # How close to center before stopping


class SimpleAI:
    """Simple AI that tracks the ball"""
    
    def __init__(self, paddle, difficulty=0.6):
        self.paddle = paddle
        self.difficulty = max(0.0, min(1.0, difficulty))
    
    def update(self, ball, delta_time):
        """Decide how to move the paddle"""
        if not ball:
            return
        
        ball_y = ball.position[1]
        paddle_center_y = self.paddle.get_center_y()
        distance = ball_y - paddle_center_y
        
        # Move toward ball if far enough away
        if abs(distance) > AI_THRESHOLD:
            if distance > 0:  # Ball below
                self.paddle.move_down()
            else:  # Ball above
                self.paddle.move_up()
        else:
            self.paddle.stop()
```

**Key Points**:
- Simple "follow the ball" strategy
- Stops when close to center (prevents jittering)
- Difficulty adjusts reaction speed (not currently used)

---

### 6. Rendering (`visuals/renderer.py`)

**Purpose**: Draws everything on screen using OpenCV.

```python
"""
renderer.py - Visual rendering (drawing the game)
"""

import cv2
import numpy as np
from .effects import VisualEffects


class Renderer:
    """Draws everything on screen"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.effects = VisualEffects(width, height)
    
    def render(self, game):
        """Create one complete frame"""
        # Create black background
        frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        overlay = frame.copy()
        
        # Draw center line
        for y in range(0, self.height, 20):
            cv2.line(overlay, 
                     (self.width // 2, y), 
                     (self.width // 2, min(y + 10, self.height)),
                     (128, 128, 128), 2)
        
        # Draw paddles (white)
        self._draw_paddle(overlay, game.paddle_left, (255, 255, 255))
        self._draw_paddle(overlay, game.paddle_right, (255, 255, 255))
        
        # Draw ball (yellow)
        self._draw_ball(overlay, game.ball, (255, 255, 0))
        
        # Blend overlay
        frame = cv2.addWeighted(frame, 0.2, overlay, 0.8, 0)
        
        # Draw score
        self._draw_bounces(frame, game.bounce_count)
        
        # Apply effects (flashes, particles)
        frame = self.effects.apply_effects(frame)
        
        return frame
    
    def _draw_paddle(self, frame, paddle, color):
        x = int(paddle.position[0])
        y = int(paddle.position[1])
        w = int(paddle.width)
        h = int(paddle.height)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
    
    def _draw_ball(self, frame, ball, color):
        center = (int(ball.position[0]), int(ball.position[1]))
        radius = int(ball.radius)
        cv2.circle(frame, center, radius, color, -1)
```

**Key Points**:
- Uses OpenCV (cv2) for drawing
- Creates numpy array (image) each frame
- Colors in BGR format (blue, green, red)

---

### 7. Settings Management (`utils/settings.py`) - ENHANCED

**Purpose**: Save/load settings to JSON file.

```python
"""
settings.py - Game settings management
"""

import json
import os

SETTINGS_FILE = "../settings.json"
DEFAULT_AUDIO_SENSITIVITY = 0.02
DEFAULT_COLOR_THEME = 'classic'
DEFAULT_DIFFICULTY = 'medium'
DEFAULT_CONTROL_MODE = 'audio'


class SettingsManager:
    """Manages game settings with JSON persistence"""

    def __init__(self, settings_file=SETTINGS_FILE):
        self.settings_file = settings_file
        self.settings = {
            'audio_sensitivity': DEFAULT_AUDIO_SENSITIVITY,
            'color_theme': DEFAULT_COLOR_THEME,
            'difficulty': DEFAULT_DIFFICULTY,
            'control_mode': DEFAULT_CONTROL_MODE
        }
        self.load_settings()

    def get_audio_sensitivity(self):
        return self.settings.get('audio_sensitivity', DEFAULT_AUDIO_SENSITIVITY)

    def set_audio_sensitivity(self, value):
        self.set('audio_sensitivity', value)

    def get_color_theme(self):
        return self.settings.get('color_theme', DEFAULT_COLOR_THEME)

    def set_color_theme(self, value):
        self.set('color_theme', value)

    def get_difficulty(self):
        return self.settings.get('difficulty', DEFAULT_DIFFICULTY)

    def set_difficulty(self, value):
        self.set('difficulty', value)

    def get_control_mode(self):
        return self.settings.get('control_mode', DEFAULT_CONTROL_MODE)

    def set_control_mode(self, value):
        self.set('control_mode', value)
```

**Key Points**:
- Now manages 4 settings (was 1)
- All settings auto-save when changed
- Persists between sessions

---

### 8. High Scores (`utils/high_scores.py`)

**Purpose**: Manage leaderboard (top 5 scores).

```python
"""
high_scores.py - High score tracking
"""

import json
import os

SCORES_FILE = "high_scores.json"
MAX_SCORES_KEPT = 5


class HighScoreManager:
    """Manages the high score leaderboard"""
    
    def __init__(self, scores_file=SCORES_FILE):
        self.scores_file = os.path.abspath(scores_file)
        self.scores = []  # List of {'name': str, 'score': int}
        self.load_scores()
    
    def load_scores(self):
        """Load high scores from JSON file"""
        if os.path.exists(self.scores_file):
            try:
                with open(self.scores_file, 'r') as f:
                    self.scores = json.load(f)
                self.scores.sort(key=lambda x: x['score'], reverse=True)
            except:
                self.scores = []
    
    def is_high_score(self, score):
        """Check if score qualifies for leaderboard"""
        if score <= 0:
            return False
        if len(self.scores) == 0:
            return True
        return score > self.scores[0]['score']
    
    def add_score(self, name, score):
        """Add new score and keep top 5"""
        self.scores.append({'name': name, 'score': score})
        self.scores.sort(key=lambda x: x['score'], reverse=True)
        self.scores = self.scores[:MAX_SCORES_KEPT]
        self.save_scores()
```

---

## 🎨 New Features (Recently Added)

### 1. Color Themes (`visuals/themes.py`)

**3 themes available:**
- **Classic** - Traditional white and yellow
- **Red Fire** - Red paddles and effects
- **Ocean Blue** - Blue and cyan colors

Change in Settings menu or programmatically:
```python
renderer.set_theme('red')  # or 'blue' or 'classic'
```

Themes affect both game display AND menu colors!

### 2. Difficulty Presets (`game/engine.py`)

**3 difficulty levels:**
- **Easy** - Slow ball (200 px/s), fast paddle, less aggressive AI
- **Medium** - Balanced (250 px/s)
- **Hard** - Fast ball (320 px/s), slower paddle, smart AI

Change in Settings menu or programmatically:
```python
game.set_difficulty('hard')  # or 'easy' or 'medium'
```

### 3. Audio Calibration Wizard (`ui/audio_calibration_dialog.py`)

**Automatic microphone calibration:**
- Step 1: Measures quiet level (3 seconds)
- Step 2: Measures loud level (3 seconds)
- Step 3: Calculates optimal threshold (30% of range)

Access via: Settings → Run Calibration Wizard

### 4. Audio Visualization (`ui/frame.py`)

**Real-time mic level display:**
- Shows volume bar below game
- Green when above threshold (paddle moves up)
- Gray when below threshold (paddle moves down)
- Displays numeric value (0.00-1.00)

### 5. Keyboard Control (`ui/frame.py`)

**Two control modes:**
- **Audio Mode** - Microphone control (default)
- **Keyboard Mode** - W/S or Arrow keys

Toggle in Settings menu. Prevents macOS error beeps!

## 🔧 Common Modifications

### Change Game Speed
In `main.py`:
```python
TIMER_INTERVAL_MS = 16  # Lower = faster, Higher = slower
```

### Change Difficulty
Use Settings menu or modify presets in `game/engine.py`:
```python
DIFFICULTY_PRESETS = {
    'easy': {
        'ball_speed': 200,
        'ai_difficulty': 0.4,
        ...
    }
}
```

### Add New Color Theme
In `visuals/themes.py`:
```python
THEMES = {
    'mytheme': {
        'name': 'My Theme',
        'paddle': (B, G, R),    # BGR for OpenCV
        'ball': (B, G, R),
        'menu_bg': (R, G, B),   # RGB for wxPython
        'menu_title': (R, G, B),
        ...
    }
}
```

### Change Microphone Sensitivity
Use Calibration Wizard or adjust in Settings menu.

### Change Window Size
In `main.py`:
```python
FIELD_WIDTH = 800   # Width in pixels
FIELD_HEIGHT = 600  # Height in pixels
```
Note: Audio viz bar adds 60px to window height automatically.

---

## 🐛 Common Issues & Solutions

### Audio Not Working
**Problem**: Paddle doesn't respond to sound
**Solution**: 
- Check microphone permissions
- Run Calibration Wizard (Settings → Run Calibration Wizard)
- Try increasing sensitivity manually in settings
- Switch to Keyboard mode temporarily to test game

### macOS Crash Loop on Restart
**Problem**: macOS asks to restore windows, then crashes repeatedly
**Solution**:
- The game now disables window restoration automatically
- If stuck in a loop, force quit and wait ~10 seconds before restarting
- Delete saved state: `rm -rf ~/Library/Saved\ Application\ State/org.python.python.savedState`

### Keyboard Not Working
**Problem**: Arrow keys make beep sound, paddle doesn't move
**Solution**:
- Make sure Control Mode is set to "Keyboard" in Settings
- The game now prevents error beeps automatically
- Both WASD and Arrow keys work

### Game Runs Too Fast/Slow
**Problem**: Inconsistent game speed
**Solution**:
- Try different difficulty settings (Settings → Difficulty)
- Check `TIMER_INTERVAL_MS` value in main.py
- Verify frame rate with logging

### Themes Look Wrong
**Problem**: Menu colors don't match game colors
**Solution**:
- Game uses BGR (OpenCV), menu uses RGB (wxPython)
- Theme colors are now properly formatted for each
- Click "Apply" in Settings to preview themes

### Settings Dialog Crashes
**Problem**: Settings dialog causes crash on macOS
**Solution**:
- Fixed by removing StaticBoxSizer (causes memory corruption on macOS 26.1)
- Now uses simple StaticText labels instead
- All widgets properly error-handled

### Ball Gets Stuck
**Problem**: Ball stuck in paddle or wall
**Solution**:
- Check collision detection logic
- Ensure ball position is corrected after collision
- Verify `_normalize_ball_velocity()` is called

### High Scores Not Saving
**Problem**: Scores lost after closing game
**Solution**:
- Check file permissions in project directory
- Verify `high_scores.json` is being created
- Check for exceptions in `save_scores()`

---

## 📝 File Structure Summary

**Game Logic**: `game/engine.py`, `game/entities.py`, `game/ai.py`
**Audio**: `audio/input_processor.py`
**Graphics**: `visuals/renderer.py`, `visuals/effects.py`, `visuals/themes.py` ⭐NEW
**UI**: `ui/frame.py`, `ui/settings_dialog.py`, `ui/game_over_dialog.py`, `ui/audio_calibration_dialog.py` ⭐NEW
**Data**: `utils/settings.py`, `utils/high_scores.py`
**Entry**: `main.py`
**Build**: `create_archive.py` (creates shareable zip)

---

## 💡 Tips for AI Assistance

When asking AI for help:

1. **Copy the relevant section** from this document
2. **Describe what you want to change**
3. **Include error messages** if something's broken
4. **Mention the file name** you're working with

Example prompt:
```
I'm working on the pong game audio system. Here's the code:

[paste audio/input_processor.py section]

I want to make it so the paddle only moves when you clap, not continuous sound. 
How can I detect sudden volume spikes instead of continuous volume?
```

---

---

## 🎮 Control Schemes

### Audio Control (Default)
- **Loud sounds** (screaming, clapping) → Paddle UP
- **Quiet/silence** → Paddle DOWN
- Sensitivity adjustable via calibration wizard or manual slider

### Keyboard Control
- **W or ↑** → Paddle UP
- **S or ↓** → Paddle DOWN
- No error beeps on macOS!

### Common Keys (Both Modes)
- **SPACE** → Pause/Resume
- **ESC** → Return to Menu
- **R** → Reset game

---

## ⚙️ Settings Overview

All settings saved to `settings.json`:

```json
{
  "audio_sensitivity": 0.04591,
  "color_theme": "classic",
  "difficulty": "medium",
  "control_mode": "audio"
}
```

**Settings Menu includes:**
- Control Mode toggle (Audio/Keyboard)
- Audio Sensitivity slider + Calibration Wizard button
- Difficulty dropdown (Easy/Medium/Hard)
- Color Theme dropdown (Classic/Red Fire/Ocean Blue)
- Apply, OK, Cancel buttons

---

**Document Version**: 2.0
**Last Updated**: January 4, 2026

**Recent Updates**:
- Added color themes system (3 themes)
- Added difficulty presets (3 levels)
- Added audio calibration wizard
- Added audio visualization widget
- Added keyboard control toggle (WASD + arrows)
- Fixed macOS compatibility issues (crash loops, error beeps)
- Enhanced settings dialog with all new options

