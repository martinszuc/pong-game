"""
input_processor.py - Audio input processing

This file listens to your microphone and converts sound into paddle movement.
The main idea is simple:
- LOUD sounds (screaming, clapping) = paddle moves UP
- QUIET/silence = paddle moves DOWN
"""

import logging
from pyo import Server, Input, Yin, RMS

logger = logging.getLogger(__name__)

# how loud a sound needs to be to move the paddle up (adjustable in settings)
DEFAULT_NOISE_THRESHOLD = 0.02

# which microphone input to use (0 = default microphone)
DEFAULT_INPUT_CHANNEL = 0

# pitch detection settings (YIN algorithm parameters)
YIN_TOLERANCE = 0.2  # how precise the pitch detection should be
YIN_MIN_FREQ = 80  # lowest frequency to detect (80 Hz)
YIN_MAX_FREQ = 1000  # highest frequency to detect (1000 Hz)

# volume measurement settings
RMS_MULTIPLIER = 10  # amplify the volume reading to make it more sensitive
VOLUME_MIN = 0.0  # quietest possible
VOLUME_MAX = 1.0  # loudest possible


class AudioInputProcessor:
    """
    processes microphone input to control the paddle
    
    this class:
    1. connects to your microphone
    2. measures how loud you are
    3. converts that into paddle movement (loud = up, quiet = down)
    """
    
    def __init__(self, server=None, noise_threshold=DEFAULT_NOISE_THRESHOLD):
        """
        create the audio processor
        
        noise_threshold: how loud you need to be for the paddle to move up
        (lower = more sensitive, higher = need to be louder)
        """
        self.server = server  # the audio server (connects to microphone)
        self.noise_threshold = noise_threshold  # sensitivity setting
        
        # these will be set up when start() is called
        self.audio_input = None  # microphone input stream
        self.pitch_detector = None  # detects pitch/frequency (not currently used)
        self.volume_rms = None  # measures volume (loudness)
        
        # current readings
        self.current_pitch = 0.0
        self.current_volume = 0.0
        
        logger.info(f"AudioInputProcessor initialized with noise_threshold={noise_threshold}")
    
    def start(self, server=None):
        """
        start listening to the microphone
        
        this connects to your default microphone and starts measuring volume
        returns True if successful, False if something went wrong
        """
        # set up the audio server if we don't have one
        if server is None:
            if self.server is None:
                self.server = Server().boot()
                self.server.start()
        else:
            self.server = server
        
        try:
            # connect to the microphone
            self.audio_input = Input(chnl=DEFAULT_INPUT_CHANNEL)
            
            # set up volume measurement (RMS = "root mean square" = average loudness)
            self.volume_rms = RMS(self.audio_input)
            
            # set up pitch detection (can detect what note you're singing)
            # note: we're not currently using pitch, just volume
            self.pitch_detector = Yin(self.audio_input, tolerance=YIN_TOLERANCE, 
                                     minfreq=YIN_MIN_FREQ, maxfreq=YIN_MAX_FREQ)
            self.pitch_detector.out()
            
            logger.info("Audio input initialized")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize audio input: {e}", exc_info=True)
            return False
    
    def get_pitch(self):
        """
        get the current pitch/frequency from the microphone
        
        this can detect what musical note you're singing (in Hz)
        returns 0.0 if no clear pitch is detected
        
        note: the game currently uses volume, not pitch
        """
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
        """
        determine which direction the paddle should move
        
        this is the main function that controls the paddle:
        - if you're LOUD (volume > threshold) → return -1 (move UP)
        - if you're quiet (volume <= threshold) → return 1 (move DOWN)
        """
        volume = self.get_volume()
        return -1 if volume > self.noise_threshold else 1
    
    def get_volume(self):
        """
        measure how loud the microphone is right now
        
        returns a number from 0.0 (silent) to 1.0 (very loud)
        this is measured using RMS (root mean square) which is the
        standard way to measure audio volume
        """
        if self.audio_input is None:
            return 0.0
        
        try:
            if self.volume_rms is not None:
                # get the RMS value and scale it to 0.0-1.0 range
                rms_value = self.volume_rms.get()
                volume = min(VOLUME_MAX, max(VOLUME_MIN, rms_value * RMS_MULTIPLIER))
            else:
                # fallback: use raw input value
                volume = abs(self.audio_input.get())
                volume = min(VOLUME_MAX, max(VOLUME_MIN, volume))
            
            self.current_volume = volume
        except Exception as e:
            logger.debug(f"Error reading volume: {e}")
            self.current_volume = 0.0
        
        return self.current_volume
    
    def stop(self):
        """stop the audio server and release the microphone"""
        if self.server is not None:
            try:
                self.server.stop()
                logger.info("Audio server stopped")
            except Exception as e:
                logger.error(f"Error stopping audio server: {e}")
