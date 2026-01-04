"""
themes.py - Color themes for the game

This file defines different color schemes (themes) for the game.
Each theme has colors for paddles, ball, background effects, etc.
"""

# theme definitions - each is a dictionary of color values
# colors are in BGR format (blue, green, red) for OpenCV

THEMES = {
    'classic': {
        'name': 'Classic',
        'paddle': (255, 255, 255),      # white
        'ball': (255, 255, 0),          # cyan/yellow
        'center_line': (128, 128, 128), # gray
        'score': (0, 0, 255),           # red
        'bg_tint': (0, 0, 0),           # black
        'particles': (255, 255, 255),   # white
        'flash_left': (255, 0, 0),      # blue (player side)
        'flash_right': (0, 255, 255),   # yellow (AI side)
        # menu colors
        'menu_bg': (30, 30, 30),        # dark gray
        'menu_title': (255, 255, 255),  # white
        'menu_text': (200, 200, 200),   # light gray
        'menu_highlight': (255, 215, 0), # gold
    },
    
    'red': {
        'name': 'Red Fire',
        'paddle': (0, 0, 255),          # red (BGR for OpenCV)
        'ball': (100, 100, 255),        # light red/pink (BGR)
        'center_line': (0, 0, 180),     # dark red (BGR)
        'score': (0, 0, 255),           # red (BGR)
        'bg_tint': (10, 0, 15),         # dark red tint (BGR)
        'particles': (100, 100, 255),   # light red (BGR)
        'flash_left': (0, 0, 255),      # red (BGR)
        'flash_right': (100, 150, 255), # orange-red (BGR)
        # menu colors - RGB format (for wxPython)
        'menu_bg': (25, 0, 0),          # dark red background RGB
        'menu_title': (255, 100, 100),  # light red/pink title RGB
        'menu_text': (200, 150, 150),   # pinkish text RGB
        'menu_highlight': (255, 50, 50), # bright red highlight RGB
    },
    
    'blue': {
        'name': 'Ocean Blue',
        'paddle': (255, 150, 0),        # blue (BGR for OpenCV)
        'ball': (255, 255, 150),        # light blue/cyan (BGR)
        'center_line': (180, 100, 0),   # darker blue (BGR)
        'score': (255, 200, 0),         # cyan (BGR)
        'bg_tint': (20, 10, 0),         # dark blue (BGR)
        'particles': (255, 200, 100),   # light blue (BGR)
        'flash_left': (255, 150, 0),    # blue (BGR)
        'flash_right': (255, 255, 150), # cyan (BGR)
        # menu colors - RGB format (for wxPython)
        'menu_bg': (0, 15, 35),         # dark blue background RGB
        'menu_title': (150, 220, 255),  # light cyan title RGB
        'menu_text': (180, 200, 220),   # light blue-gray text RGB
        'menu_highlight': (100, 200, 255), # bright cyan highlight RGB
    }
}


def get_theme(theme_name):
    """
    get a theme by name
    
    if the theme doesn't exist, returns the classic theme
    """
    return THEMES.get(theme_name, THEMES['classic'])


def get_theme_names():
    """get a list of all available theme names"""
    return list(THEMES.keys())


def get_theme_display_names():
    """get a list of theme display names (prettier names for UI)"""
    return [theme['name'] for theme in THEMES.values()]

