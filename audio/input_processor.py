import logging
from pyo import Server, Input, Yin, RMS

logger = logging.getLogger(__name__)

DEFAULT_NOISE_THRESHOLD = 0.02
DEFAULT_INPUT_CHANNEL = 0
YIN_TOLERANCE = 0.2
YIN_MIN_FREQ = 80
YIN_MAX_FREQ = 1000
RMS_MULTIPLIER = 10
VOLUME_MIN = 0.0
VOLUME_MAX = 1.0


class AudioInputProcessor:
    def __init__(self, server=None, noise_threshold=DEFAULT_NOISE_THRESHOLD):
        self.server = server
        self.noise_threshold = noise_threshold
        self.audio_input = None
        self.pitch_detector = None
        self.volume_rms = None
        self.current_pitch = 0.0
        self.current_volume = 0.0
        logger.info(f"AudioInputProcessor initialized with noise_threshold={noise_threshold}")
    
    def start(self, server=None):
        if server is None:
            if self.server is None:
                self.server = Server().boot()
                self.server.start()
        else:
            self.server = server
        
        try:
            self.audio_input = Input(chnl=DEFAULT_INPUT_CHANNEL)
            self.volume_rms = RMS(self.audio_input)
            self.pitch_detector = Yin(self.audio_input, tolerance=YIN_TOLERANCE, 
                                     minfreq=YIN_MIN_FREQ, maxfreq=YIN_MAX_FREQ)
            self.pitch_detector.out()
            logger.info("Audio input initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize audio input: {e}", exc_info=True)
            return False
    
    def get_pitch(self):
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
        volume = self.get_volume()
        return -1 if volume > self.noise_threshold else 1
    
    def get_volume(self):
        if self.audio_input is None:
            return 0.0
        
        try:
            if self.volume_rms is not None:
                rms_value = self.volume_rms.get()
                volume = min(VOLUME_MAX, max(VOLUME_MIN, rms_value * RMS_MULTIPLIER))
            else:
                volume = abs(self.audio_input.get())
                volume = min(VOLUME_MAX, max(VOLUME_MIN, volume))
            self.current_volume = volume
        except Exception as e:
            logger.debug(f"Error reading volume: {e}")
            self.current_volume = 0.0
        
        return self.current_volume
    
    def stop(self):
        if self.server is not None:
            try:
                self.server.stop()
                logger.info("Audio server stopped")
            except Exception as e:
                logger.error(f"Error stopping audio server: {e}")
