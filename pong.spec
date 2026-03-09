# pong.spec - PyInstaller build configuration
#
# Usage:
#   pip install pyinstaller
#   pyinstaller pong.spec
#
# Output:
#   dist/PongGame          (Linux/macOS binary)
#   dist/PongGame.app      (macOS app bundle)
#   dist/PongGame.exe      (Windows executable)

import sys
import platform
from pathlib import Path

block_cipher = None

# Collect all hidden imports that PyInstaller might miss
hidden_imports = [
    'wx',
    'cv2',
    'numpy',
    'sounddevice',
    'audio.input_processor',
    'game.engine',
    'game.entities',
    'game.ai',
    'visuals.renderer',
    'visuals.effects',
    'visuals.themes',
    'ui.frame',
    'ui.settings_dialog',
    'ui.game_over_dialog',
    'ui.audio_calibration_dialog',
    'utils.settings',
    'utils.high_scores',
    'utils.logger',
    'lighting.artnet_controller',
    '_sounddevice_data',
]

# Add pyo only on macOS (it's macOS-only in this project)
if platform.system() == 'Darwin':
    hidden_imports += ['pyo', 'pyo64']

a = Analysis(
    ['main.py'],
    pathex=[str(Path('.').resolve())],
    binaries=[],
    datas=[
        # Include any data files your app needs at runtime
        # ('assets/', 'assets/'),  # uncomment if you have an assets folder
    ],
    hiddenimports=hidden_imports,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        'tkinter',      # not used
        'matplotlib',   # not used
        'scipy',        # not used
        'PIL',          # not used
        'IPython',      # not used
    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PongGame',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,        # no console window popup on Windows
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,            # add 'assets/icon.ico' here if you have one
)

coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PongGame',
)

# macOS: also bundle as a .app
if platform.system() == 'Darwin':
    app = BUNDLE(
        coll,
        name='PongGame.app',
        icon=None,            # add 'assets/icon.icns' here if you have one
        bundle_identifier='com.yourname.ponggame',
        info_plist={
            'NSMicrophoneUsageDescription': 'Microphone is used to control the game paddle.',
            'CFBundleShortVersionString': '1.0.0',
            'CFBundleName': 'Pong Game',
            'LSMinimumSystemVersion': '12.0',
            'NSHighResolutionCapable': True,
        },
    )
