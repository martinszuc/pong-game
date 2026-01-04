"""
main.py - The entry point of the audio-controlled pong game

This file starts the entire game application. It sets up all the necessary 
components (audio, graphics, game logic) and runs the main game loop.
"""

import wx  # wxPython - creates windows and user interface
import time  # helps us track how much time passes between frames
import sys  # system operations like exiting the program
import logging  # records what's happening in the game (for debugging)
import platform  # tells us what operating system we're running on

# import our custom game components
from game.engine import PongGame  # the game rules and physics
from visuals.renderer import Renderer  # draws the game on screen
from ui.frame import PongFrame  # the main window
from utils.logger import setup_logging, get_logger  # logging helpers

# pyo is optional (used on macOS, sounddevice used on Linux/Windows)
PYO_AVAILABLE = False
Server = None

try:
    from pyo import Server  # audio processing library
    PYO_AVAILABLE = True
except ImportError:
    pass  # sounddevice will be used instead

# detect which operating system we're on (different OS need different settings)
IS_MACOS = platform.system() == 'Darwin'
IS_LINUX = platform.system() == 'Linux'
IS_WINDOWS = platform.system() == 'Windows'

# game window size in pixels
FIELD_WIDTH = 800
FIELD_HEIGHT = 600

# how often to update the game (16ms = approximately 60 frames per second)
# Windows: use 20ms to reduce flickering (50 FPS instead of 60)
TIMER_INTERVAL_MS = 20 if platform.system() == 'Windows' else 16

# maximum time jump between updates (prevents weird behavior if computer lags)
MAX_DELTA_TIME = 0.1

setup_logging()  # start recording what happens in the game
logger = get_logger(__name__)


class PongApplication:
    """
    the main application class - this sets up and runs the entire pong game
    
    think of this as the "conductor" of an orchestra - it makes sure all the
    different parts (audio, graphics, game logic) work together smoothly
    """
    
    def __init__(self):
        """
        initialize the application - this runs when the game first starts
        sets up all the components we need: audio, graphics, game engine, etc.
        """
        logger.info("Initializing Pong Application")
        logger.info(f"Platform: {platform.system()} ({platform.platform()})")
        
        # store the game field dimensions
        self.field_width = FIELD_WIDTH
        self.field_height = FIELD_HEIGHT
        
        # initialize all the components (order matters - some depend on others)
        self._init_wx_app()  # create the window system
        self._init_audio()  # set up microphone input
        self._init_lighting()  # set up DMX lighting (optional)
        self._init_game()  # create the game engine and renderer
        self._init_ui()  # create the window and interface
        self._init_timer()  # start the game loop timer
        
        logger.info("Application initialized successfully")
    
    def _init_wx_app(self):
        """create the wxPython application (the window system)"""
        try:
            # on macOS, suppress redirect to avoid autorelease pool warnings
            self.app = wx.App(redirect=False) if IS_MACOS else wx.App()
            
            # disable macOS window restoration (prevents crash loops on reopen)
            if IS_MACOS:
                self.app.SetExitOnFrameDelete(True)
                # tell macOS not to restore windows after crash
                try:
                    import objc  # type: ignore
                    from Foundation import NSUserDefaults  # type: ignore
                    defaults = NSUserDefaults.standardUserDefaults()
                    defaults.setBool_forKey_(False, "NSQuitAlwaysKeepsWindows")
                except Exception:
                    # if Foundation not available, that's ok - continue anyway
                    pass
            
            logger.info("wx.App created successfully")
        except Exception as e:
            logger.error(f"Failed to create wx.App: {e}", exc_info=True)
            raise
    
    def _init_audio(self):
        """
        set up the audio system for microphone input
        
        the game uses your microphone to control the left paddle:
        - loud sounds (screaming, clapping) = paddle moves up
        - quiet/silence = paddle moves down
        
        if audio is not available, the game defaults to keyboard mode
        """
        from utils.settings import SettingsManager
        self.settings = SettingsManager()
        
        # start audio server (pyo on macOS, sounddevice doesn't need one)
        if PYO_AVAILABLE:
            try:
                # start the audio server (this connects to your microphone)
                self.audio_server = Server().boot()
                self.audio_server.start()
                logger.info("Audio server started (pyo)")
            except Exception as e:
                logger.error(f"Failed to start audio server: {e}", exc_info=True)
                if IS_MACOS:
                    logger.error("On macOS, you may need to run: ./fix_flac.sh")
                self.audio_server = None
        else:
            # sounddevice doesn't need a server
            self.audio_server = None
            logger.info("Using sounddevice for audio (no server needed)")
        
        from audio.input_processor import AudioInputProcessor
        
        # load settings (like how sensitive the microphone should be)
        audio_sensitivity = self.settings.get_audio_sensitivity()
        
        # create the audio processor that listens to your microphone
        self.audio_input = AudioInputProcessor(server=self.audio_server, noise_threshold=audio_sensitivity)
        
        # start listening to the microphone
        try:
            if self.audio_input.start(self.audio_server):
                logger.info("Audio input ready")
            else:
                logger.warning("Audio input failed to start - keyboard mode available")
                self.audio_input = None
        except Exception as e:
            logger.error(f"Error starting audio input: {e}")
            self.audio_input = None
    
    def _init_lighting(self):
        """
        set up DMX lighting control (optional feature)
        
        if you have DMX lights connected, they'll flash and change colors
        when the ball hits paddles or walls. if no lights are connected,
        the game still works fine - this is just a bonus visual effect
        """
        try:
            from lighting.artnet_controller import ArtNetController
            self.lighting = ArtNetController(target_ip='127.0.0.1', universe=0)
            self.lighting.connect()
        except Exception as e:
            logger.warning(f"Failed to initialize lighting: {e}")
            self.lighting = None
    
    def _init_game(self):
        """
        create the game engine and renderer
        
        the game engine handles all the physics (ball movement, collisions)
        the renderer draws everything on screen (ball, paddles, effects)
        """
        # get saved settings
        difficulty = self.settings.get_difficulty()
        theme = self.settings.get_color_theme()
        
        # create the game engine (the "brain" that runs the game logic)
        self.game = PongGame(self.field_width, self.field_height, difficulty=difficulty)
        
        # create the renderer (the "artist" that draws everything)
        self.renderer = Renderer(self.field_width, self.field_height, theme_name=theme)
        
        # connect the game engine to the renderer so it knows when to draw trails
        self.game.set_trail_callbacks(
            self.renderer.paint_trail,
            self.renderer.change_trail_color
        )
        
        # tell the game engine to trigger visual effects when things happen
        self.game.set_visual_callbacks(
            goal_flash=lambda player_left: self.renderer.trigger_goal_flash(player_left),
            paddle_hit=lambda x, y: self.renderer.trigger_collision_particles(x, y),
            wall_bounce=lambda x, y: self.renderer.trigger_collision_particles(x, y)
        )
        
        # if we have lighting, connect it to game events too
        if self.lighting:
            self.game.set_lighting_callbacks(
                goal_flash=lambda player_left: self.lighting.goal_flash(player_left),
                collision_flash=lambda: self.lighting.collision_flash()
            )
    
    def _init_ui(self):
        """
        create the main game window
        
        this creates the window you see on screen with the game display,
        menu buttons, and all the user interface elements
        """
        try:
            logger.info("Creating main window...")
            self.frame = PongFrame(
                self.game, 
                self.renderer, 
                on_close_callback=self.on_close,
                lighting=self.lighting,
                audio_input=self.audio_input,
                settings=self.settings
            )
            logger.info("Main window created successfully")
        except Exception as e:
            logger.error(f"Failed to create main window: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
            raise
    
    def _init_timer(self):
        """
        start the game loop timer
        
        this timer fires 60 times per second (every 16 milliseconds)
        each time it fires, we update the game and redraw everything
        this is what makes the game animated and smooth
        """
        self.running = True
        self.last_time = time.time()  # remember when we started
        self.timer = wx.Timer(self.frame)  # create the timer
        self.frame.Bind(wx.EVT_TIMER, self.on_timer, self.timer)  # connect timer to our update function
        self.timer.Start(TIMER_INTERVAL_MS)  # start firing every 16ms
    
    def on_close(self):
        """
        clean up when the game is closed
        
        this stops all the running systems (audio, lighting, timer)
        before the program exits. it's important to clean up properly
        so the microphone and other resources are released
        """
        self.running = False
        self.timer.Stop()  # stop the game loop
        
        # stop the microphone
        if self.audio_input:
            self.audio_input.stop()
        
        # disconnect the lights
        if self.lighting:
            try:
                self.lighting.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting lighting: {e}")
        
        # stop the audio server
        if self.audio_server:
            try:
                self.audio_server.stop()
            except:
                pass
    
    def on_timer(self, event):
        """
        the main game loop - this runs 60 times per second
        
        each frame, we:
        1. check the microphone and move the paddle
        2. update the game physics (ball position, collisions)
        3. update visual effects (particles, flashes)
        4. redraw everything on screen
        """
        if not self.running:
            return
        
        try:
            # calculate how much time passed since the last frame
            # (this helps keep the game speed consistent even if framerate varies)
            current_time = time.time()
            delta_time = min(current_time - self.last_time, MAX_DELTA_TIME)
            self.last_time = current_time
            
            # if the game is playing, control the paddle
            if self.game.game_state == 'playing':
                # check control mode (audio or keyboard)
                control_mode = self.settings.get_control_mode()
                
                if control_mode == 'keyboard':
                    # keyboard control is handled in the frame's check_movement_keys method
                    pass
                elif self.audio_input:
                    # audio control
                    paddle_dir = self.audio_input.get_paddle_direction()
                    if paddle_dir == -1:  # loud sound detected
                        self.game.paddle_left.move_up()
                    elif paddle_dir == 1:  # quiet/silence
                        self.game.paddle_left.move_down()
            elif self.game.game_state == 'paused':
                self.game.paddle_left.stop()  # don't move paddle when paused
            
            # update visual effects (particles fade out, flashes dim, etc.)
            self.renderer.update_effects(delta_time)
            
            # update game physics (move ball, check collisions, update score)
            self.game.update(delta_time)
            
            # draw everything to create the current frame
            frame = self.renderer.render(self.game)
            
            # make sure we got a valid frame
            if frame is None or frame.size == 0:
                logger.error("Renderer returned invalid frame")
                return
            
            # display the frame in the window
            self.frame.update_display(frame)
            
        except Exception as e:
            logger.error(f"Error in game loop: {e}", exc_info=True)
    
    def run(self):
        """
        start the application main loop
        
        this renders the first frame and then starts the wxPython event loop,
        which keeps the window open and responding to user actions
        """
        try:
            logger.info("Rendering initial frame...")
            # render and display the initial frame (before the game starts)
            frame = self.renderer.render(self.game)
            if frame is not None:
                self.frame.update_display(frame)
                self.frame.Refresh()
            logger.info("Initial frame rendered successfully")
        except Exception as e:
            logger.error(f"Error rendering initial frame: {e}", exc_info=True)
            import traceback
            traceback.print_exc()
        
        logger.info("Starting main event loop...")
        # start the main event loop (this keeps the window open and running)
        try:
            self.app.MainLoop()
        except Exception as e:
            logger.error(f"Error in main loop: {e}", exc_info=True)
            import traceback
            traceback.print_exc()


def main():
    """
    the program entry point - this is what runs when you start the game
    """
    try:
        logger.info("=" * 50)
        logger.info("Starting Audio-Controlled Pong Game")
        logger.info("=" * 50)
        
        # create and run the application
        app = PongApplication()
        app.run()
        
        logger.info("Game exited normally")
    except KeyboardInterrupt:
        # user pressed Ctrl+C to quit
        logger.info("Game interrupted by user")
        sys.exit(0)
    except Exception as e:
        # something went wrong - log the error and exit
        logger.critical(f"Fatal error: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


# this runs when the script is executed directly (not imported as a module)
if __name__ == "__main__":
    main()
