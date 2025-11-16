"""Audio input processing for paddle control"""

import logging
from pyo import Server, Input, Yin, RMS

logger = logging.getLogger(__name__)


class AudioInputProcessor:
    """Processes microphone input - paddle falls down by default, noise raises it up"""
    
    def __init__(self, server=None, noise_threshold=0.02):
        """
        Args:
            server: pyo Server instance
            noise_threshold: Volume threshold (0.0-1.0) - lower = more sensitive
                           Default 0.02 (2%) for normal voice detection
        """
        self.server = server
        self.noise_threshold = noise_threshold
        self.audio_input = None
        self.pitch_detector = None
        self.volume_rms = None
        self.current_pitch = 0.0
        self.current_volume = 0.0
        logger.info(f"AudioInputProcessor initialized with noise_threshold={noise_threshold}")
    
    def start(self, server=None):
        """Initialize audio input"""
        if server is None:
            if self.server is None:
                self.server = Server().boot()
                self.server.start()
        else:
            self.server = server
        
        try:
            self.audio_input = Input(chnl=0)
            self.volume_rms = RMS(self.audio_input)
            self.pitch_detector = Yin(self.audio_input, tolerance=0.2, minfreq=80, maxfreq=1000)
            self.pitch_detector.out()
            logger.info("Audio input initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize audio input: {e}", exc_info=True)
            return False
    
    def get_pitch(self):
        """Get current detected pitch in Hz"""
        if self.pitch_detector is None:
            return 0.0
        
        try:
            pitch_value = self.pitch_detector.get()
            if pitch_value is not None and pitch_value > 0:
                self.current_pitch = float(pitch_value)
            else:
                self.current_pitch = 0.0
        except Exception as e:
            logger.debug(f"Error reading pitch: {e}")
            self.current_pitch = 0.0
        
        return self.current_pitch
    
    def get_paddle_direction(self):
        """Returns -1 (up) if noise detected, 1 (down) otherwise"""
        volume = self.get_volume()
        return -1 if volume > self.noise_threshold else 1
    
    def get_volume(self):
        """Get current audio input volume using RMS (0.0 to 1.0)"""
        if self.audio_input is None:
            return 0.0
        
        try:
            if self.volume_rms is not None:
                rms_value = self.volume_rms.get()
                volume = min(1.0, max(0.0, rms_value * 10))
            else:
                volume = abs(self.audio_input.get())
                volume = min(1.0, max(0.0, volume))
            self.current_volume = volume
        except Exception as e:
            logger.debug(f"Error reading volume: {e}")
            self.current_volume = 0.0
        
        return self.current_volume
    
    def stop(self):
        """Stop audio processing"""
        if self.server is not None:
            try:
                self.server.stop()
                logger.info("Audio server stopped")
            except Exception as e:
                logger.error(f"Error stopping audio server: {e}")
