import wx
import time
import sys
import logging
import platform

from game.engine import PongGame
from visuals.renderer import Renderer
from ui.frame import PongFrame
from utils.logger import setup_logging, get_logger
from pyo import Server

IS_MACOS = platform.system() == 'Darwin'
IS_LINUX = platform.system() == 'Linux'
IS_WINDOWS = platform.system() == 'Windows'

FIELD_WIDTH = 800
FIELD_HEIGHT = 600
TIMER_INTERVAL_MS = 16
MAX_DELTA_TIME = 0.1

setup_logging()
logger = get_logger(__name__)


class PongApplication:
    def __init__(self):
        logger.info("Initializing Pong Application")
        logger.info(f"Platform: {platform.system()} ({platform.platform()})")
        
        self.field_width = FIELD_WIDTH
        self.field_height = FIELD_HEIGHT
        
        self._init_wx_app()
        self._init_audio()
        self._init_lighting()
        self._init_game()
        self._init_ui()
        self._init_timer()
        
        logger.info("Application initialized successfully")
    
    def _init_wx_app(self):
        try:
            self.app = wx.App()
            logger.info("wx.App created successfully")
        except Exception as e:
            logger.error(f"Failed to create wx.App: {e}", exc_info=True)
            raise
    
    def _init_audio(self):
        try:
            self.audio_server = Server().boot()
            self.audio_server.start()
            logger.info("Audio server started")
        except Exception as e:
            logger.error(f"Failed to start audio server: {e}", exc_info=True)
            if IS_MACOS:
                logger.error("On macOS, you may need to run: ./fix_flac.sh")
            self.audio_server = None
        
        from audio.input_processor import AudioInputProcessor
        from utils.settings import SettingsManager
        
        self.settings = SettingsManager()
        audio_sensitivity = self.settings.get_audio_sensitivity()
        self.audio_input = AudioInputProcessor(server=self.audio_server, noise_threshold=audio_sensitivity)
        
        if self.audio_server is not None:
            self.audio_input.start(self.audio_server)
    
    def _init_lighting(self):
        try:
            from lighting.artnet_controller import ArtNetController
            self.lighting = ArtNetController(target_ip='127.0.0.1', universe=0)
            self.lighting.connect()
        except Exception as e:
            logger.warning(f"Failed to initialize lighting: {e}")
            self.lighting = None
    
    def _init_game(self):
        self.game = PongGame(self.field_width, self.field_height)
        self.renderer = Renderer(self.field_width, self.field_height)
        
        self.game.set_trail_callbacks(
            self.renderer.paint_trail,
            self.renderer.change_trail_color
        )
        
        self.game.set_visual_callbacks(
            goal_flash=lambda player_left: self.renderer.trigger_goal_flash(player_left),
            paddle_hit=lambda x, y: self.renderer.trigger_collision_particles(x, y),
            wall_bounce=lambda x, y: self.renderer.trigger_collision_particles(x, y)
        )
        
        if self.lighting:
            self.game.set_lighting_callbacks(
                goal_flash=lambda player_left: self.lighting.goal_flash(player_left),
                collision_flash=lambda: self.lighting.collision_flash()
            )
    
    def _init_ui(self):
        try:
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
            raise
    
    def _init_timer(self):
        self.running = True
        self.last_time = time.time()
        self.timer = wx.Timer(self.frame)
        self.frame.Bind(wx.EVT_TIMER, self.on_timer, self.timer)
        self.timer.Start(TIMER_INTERVAL_MS)
    
    def on_close(self):
        self.running = False
        self.timer.Stop()
        
        if self.audio_input:
            self.audio_input.stop()
        if self.lighting:
            try:
                self.lighting.disconnect()
            except Exception as e:
                logger.error(f"Error disconnecting lighting: {e}")
        if self.audio_server:
            try:
                self.audio_server.stop()
            except:
                pass
    
    def on_timer(self, event):
        if not self.running:
            return
        
        try:
            current_time = time.time()
            delta_time = min(current_time - self.last_time, MAX_DELTA_TIME)
            self.last_time = current_time
            
            if self.game.game_state == 'playing' and self.audio_input:
                paddle_dir = self.audio_input.get_paddle_direction()
                if paddle_dir == -1:
                    self.game.paddle_left.move_up()
                elif paddle_dir == 1:
                    self.game.paddle_left.move_down()
            elif self.game.game_state == 'paused':
                self.game.paddle_left.stop()
            
            self.renderer.update_effects(delta_time)
            self.game.update(delta_time)
            frame = self.renderer.render(self.game)
            
            if frame is None or frame.size == 0:
                logger.error("Renderer returned invalid frame")
                return
            
            self.frame.update_display(frame)
            
        except Exception as e:
            logger.error(f"Error in game loop: {e}", exc_info=True)
    
    def run(self):
        try:
            frame = self.renderer.render(self.game)
            if frame is not None:
                self.frame.update_display(frame)
                self.frame.Refresh()
        except Exception as e:
            logger.error(f"Error rendering initial frame: {e}", exc_info=True)
        
        self.app.MainLoop()


def main():
    try:
        logger.info("=" * 50)
        logger.info("Starting Audio-Controlled Pong Game")
        logger.info("=" * 50)
        
        app = PongApplication()
        app.run()
        
        logger.info("Game exited normally")
    except KeyboardInterrupt:
        logger.info("Game interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.critical(f"Fatal error: {e}", exc_info=True)
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    main()
