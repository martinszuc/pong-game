import json
import os
import logging

logger = logging.getLogger(__name__)

SETTINGS_FILE = "settings.json"
DEFAULT_AUDIO_SENSITIVITY = 0.02


class SettingsManager:
    def __init__(self, settings_file=SETTINGS_FILE):
        self.settings_file = settings_file
        self.settings = {
            'audio_sensitivity': DEFAULT_AUDIO_SENSITIVITY
        }
        self.load_settings()
    
    def load_settings(self):
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    loaded = json.load(f)
                    self.settings.update(loaded)
                logger.info(f"Loaded settings from {self.settings_file}")
            except Exception as e:
                logger.error(f"Error loading settings: {e}")
                self.save_settings()
        else:
            self.save_settings()
    
    def save_settings(self):
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info(f"Saved settings to {self.settings_file}")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        return self.settings.get(key, default)
    
    def set(self, key, value):
        self.settings[key] = value
        self.save_settings()
    
    def get_audio_sensitivity(self):
        return self.settings.get('audio_sensitivity', DEFAULT_AUDIO_SENSITIVITY)
    
    def set_audio_sensitivity(self, value):
        self.set('audio_sensitivity', value)

