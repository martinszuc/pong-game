"""
input_processor.py - Audio input processing

This file listens to your microphone and converts sound into paddle movement.
The main idea is simple:
- LOUD sounds (screaming, clapping) = paddle moves UP
- QUIET/silence = paddle moves DOWN

Uses pyo on macOS (better performance) or sounddevice on Linux/Windows (easier install).
"""

import logging
import numpy as np

# try pyo first (macOS), fall back to sounddevice (cross-platform)
USE_PYO = False
try:
    from pyo import Server, Input, Yin, RMS
    USE_PYO = True
except ImportError:
    try:
        import sounddevice as sd
    except ImportError:
        pass  # will handle in start() method

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
    
    uses pyo on macOS, sounddevice on Linux/Windows (cross-platform)
    """
    
    def __init__(self, server=None, noise_threshold=DEFAULT_NOISE_THRESHOLD):
        """
        create the audio processor
        
        noise_threshold: how loud you need to be for the paddle to move up
        (lower = more sensitive, higher = need to be louder)
        """
        self.server = server  # the audio server (connects to microphone) - pyo only
        self.noise_threshold = noise_threshold  # sensitivity setting
        
        # pyo-specific (macOS)
        self.audio_input = None  # microphone input stream
        self.pitch_detector = None  # detects pitch/frequency (not currently used)
        self.volume_rms = None  # measures volume (loudness)
        
        # sounddevice-specific (Linux/Windows)
        self.stream = None  # audio input stream
        self.audio_buffer = []  # recent audio samples
        
        # current readings
        self.current_pitch = 0.0
        self.current_volume = 0.0
        
        backend = 'pyo (optimized)' if USE_PYO else 'sounddevice (cross-platform)'
        logger.info(f"AudioInputProcessor initialized with noise_threshold={noise_threshold}, using {backend}")
    
    def start(self, server=None):
        """
        start listening to the microphone
        
        this connects to your default microphone and starts measuring volume
        returns True if successful, False if something went wrong
        """
        if USE_PYO:
            return self._start_pyo(server)
        else:
            return self._start_sounddevice()
    
    def _start_pyo(self, server=None):
        """start using pyo (macOS) - original implementation"""
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
            
            logger.info("Audio input initialized (pyo)")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize pyo audio input: {e}", exc_info=True)
            return False
    
    def _start_sounddevice(self):
        """start using sounddevice (Linux/Windows)"""
        try:
            # callback function that receives audio data
            def audio_callback(indata, frames, time, status):
                if status:
                    logger.warning(f"Audio callback status: {status}")
                # calculate RMS volume from audio data
                volume = np.sqrt(np.mean(indata**2))
                self.current_volume = float(volume)
            
            # open input stream with default microphone
            self.stream = sd.InputStream(
                channels=1,
                callback=audio_callback,
                blocksize=1024,
                samplerate=44100
            )
            self.stream.start()
            
            logger.info("Audio input initialized (sounddevice)")
            return True
        except Exception as e:
            logger.error(f"Failed to initialize sounddevice audio input: {e}", exc_info=True)
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
        if USE_PYO:
            return self._get_volume_pyo()
        else:
            return self._get_volume_sounddevice()
    
    def _get_volume_pyo(self):
        """get volume using pyo (original implementation)"""
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
    
    def _get_volume_sounddevice(self):
        """get volume using sounddevice (updated by callback)"""
        # current_volume is updated by the audio callback
        # scale it to match pyo's range
        volume = min(VOLUME_MAX, max(VOLUME_MIN, self.current_volume * RMS_MULTIPLIER))
        return volume
    
    def stop(self):
        """stop the audio server and release the microphone"""
        if USE_PYO and self.server is not None:
            try:
                self.server.stop()
                logger.info("Audio server stopped (pyo)")
            except Exception as e:
                logger.error(f"Error stopping audio server: {e}")
        elif not USE_PYO and self.stream is not None:
            try:
                self.stream.stop()
                self.stream.close()
                logger.info("Audio stream stopped (sounddevice)")
            except Exception as e:
                logger.error(f"Error stopping audio stream: {e}")
