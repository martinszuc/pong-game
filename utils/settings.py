"""
settings.py - Game settings management

This file handles saving and loading game settings (like microphone sensitivity).
Settings are stored in a JSON file so they persist between game sessions.
"""

import json
import os
import logging

logger = logging.getLogger(__name__)

# where to save the settings
SETTINGS_FILE = "settings.json"

# default microphone sensitivity (how loud you need to be)
DEFAULT_AUDIO_SENSITIVITY = 0.02

# default color theme
DEFAULT_COLOR_THEME = 'classic'

# default difficulty preset
DEFAULT_DIFFICULTY = 'medium'

# default control mode (audio or keyboard)
DEFAULT_CONTROL_MODE = 'audio'


class SettingsManager:
    """
    manages game settings (saving and loading)
    
    settings are stored in a JSON file on your computer so they're
    remembered the next time you play
    """
    
    def __init__(self, settings_file=SETTINGS_FILE):
        """
        create the settings manager
        automatically loads saved settings if they exist
        """
        self.settings_file = settings_file
        
        # default settings (used if no save file exists)
        self.settings = {
            'audio_sensitivity': DEFAULT_AUDIO_SENSITIVITY,
            'color_theme': DEFAULT_COLOR_THEME,
            'difficulty': DEFAULT_DIFFICULTY,
            'control_mode': DEFAULT_CONTROL_MODE
        }
        
        # try to load saved settings
        self.load_settings()
    
    def load_settings(self):
        """
        load settings from the JSON file
        if the file doesn't exist or is corrupted, use default settings
        """
        if os.path.exists(self.settings_file):
            try:
                # open and read the JSON file
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)  # merge loaded settings with defaults
                logger.info(f"Loaded settings from {self.settings_file}")
            except Exception as e:
                # file is corrupted or unreadable - use defaults and save them
                logger.error(f"Error loading settings: {e}")
                self.save_settings()
        else:
            # no settings file exists yet - create one with defaults
            self.save_settings()
    
    def save_settings(self):
        """
        save current settings to the JSON file
        indent=2 makes the file human-readable
        """
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info(f"Saved settings to {self.settings_file}")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        """get a setting value by name (returns default if not found)"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """set a setting value and immediately save to disk"""
        self.settings[key] = value
        self.save_settings()
    
    def get_audio_sensitivity(self):
        """get the microphone sensitivity setting"""
        return self.settings.get('audio_sensitivity', DEFAULT_AUDIO_SENSITIVITY)
    
    def set_audio_sensitivity(self, value):
        """set the microphone sensitivity and save it"""
        self.set('audio_sensitivity', value)
    
    def get_color_theme(self):
        """get the current color theme"""
        return self.settings.get('color_theme', DEFAULT_COLOR_THEME)
    
    def set_color_theme(self, value):
        """set the color theme and save it"""
        self.set('color_theme', value)
    
    def get_difficulty(self):
        """get the current difficulty preset"""
        return self.settings.get('difficulty', DEFAULT_DIFFICULTY)
    
    def set_difficulty(self, value):
        """set the difficulty preset and save it"""
        self.set('difficulty', value)
    
    def get_control_mode(self):
        """get the current control mode (audio or keyboard)"""
        return self.settings.get('control_mode', DEFAULT_CONTROL_MODE)
    
    def set_control_mode(self, value):
        """set the control mode and save it"""
        self.set('control_mode', value)

