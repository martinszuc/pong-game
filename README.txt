Audio-Controlled Pong Game
============================

Course: B0B39MM1 Multimedia 1, CTU FEL Prague
Team: Tereza Neveselá & Marco Balducci

QUICK START
-----------
For macOS/Linux:
  bash setup.sh      # First time setup
  bash run.sh        # Run the game

For Windows:
  setup.bat          # First time setup
  run.bat            # Run the game

MANUAL SETUP
------------
1. Install Python 3.8 or higher
   - Check: python3 --version (or python --version on Windows)
   - Download from: https://www.python.org/downloads/

2. Create and activate virtual environment:

   macOS/Linux:
     python3 -m venv venv
     source venv/bin/activate

   Windows:
     python -m venv venv
     venv\Scripts\activate.bat

3. Install dependencies:
   pip install --upgrade pip
   pip install -r requirements.txt

   Note: pyo installation may require additional system dependencies:
   - macOS: brew install portaudio
   - Linux: sudo apt-get install portaudio19-dev python3-dev
   - Windows: usually handled by pip (may need Visual C++ Redistributable)

4. Run the game:
   python main.py

5. Deactivate virtual environment when done:
   deactivate

CURRENT FEATURES (Phase 1, Milestone 1)
---------------------------------------
- Basic Pong game mechanics
- Keyboard controls:
  - W/S: Left paddle up/down
  - Up/Down arrows: Right paddle up/down
  - Space: Pause/Resume
- Score tracking
- Paddle and ball physics with collision detection

UPCOMING FEATURES
-----------------
- Webcam background integration
- Audio input (pitch detection for paddle control)
- Synthesized sound effects
- Visual effects (particles, goal flashes)
- ArtNET/DMX lighting control
- Volume slider integration

PLATFORM SUPPORT
----------------
Tested on: macOS, Linux, Windows (Python 3.8+)

TROUBLESHOOTING
---------------
- If wxPython fails to install, try: pip install wxpython
- If OpenCV import fails, try: pip install opencv-python-headless
- Ensure camera/microphone permissions are granted when audio/webcam features are added

