"""Settings management with JSON storage"""

import json
import os
import logging

logger = logging.getLogger(__name__)

SETTINGS_FILE = "settings.json"


class SettingsManager:
    """Manages application settings stored in JSON file"""
    
    def __init__(self, settings_file=SETTINGS_FILE):
        self.settings_file = settings_file
        self.settings = {
            'audio_sensitivity': 0.02,
            'master_volume': 0.5,
            'ai_enabled': True
        }
        self.load_settings()
    
    def load_settings(self):
        """Load settings from JSON file"""
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
        """Save settings to JSON file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=2)
            logger.info(f"Saved settings to {self.settings_file}")
        except Exception as e:
            logger.error(f"Error saving settings: {e}")
    
    def get(self, key, default=None):
        """Get a setting value"""
        return self.settings.get(key, default)
    
    def set(self, key, value):
        """Set a setting value and save"""
        self.settings[key] = value
        self.save_settings()
    
    def get_audio_sensitivity(self):
        """Get audio sensitivity threshold"""
        return self.settings.get('audio_sensitivity', 0.02)
    
    def set_audio_sensitivity(self, value):
        """Set audio sensitivity threshold"""
        self.set('audio_sensitivity', value)
    
    def get_master_volume(self):
        """Get master volume"""
        return self.settings.get('master_volume', 0.5)
    
    def set_master_volume(self, value):
        """Set master volume"""
        self.set('master_volume', value)
    
    def get_ai_enabled(self):
        """Get AI enabled state"""
        return self.settings.get('ai_enabled', True)
    
    def set_ai_enabled(self, value):
        """Set AI enabled state"""
        self.set('ai_enabled', value)

