"""
Main entry point for Audio-Controlled Pong Game
"""

import wx
import cv2
import time
import sys
import logging

from game.engine import PongGame
from visuals.renderer import Renderer
from ui.interface import PongFrame
from utils.logger import setup_logging, get_logger

# Setup logging
setup_logging()
logger = get_logger(__name__)


class PongApplication:
    """Main application class managing game loop and integration"""
    
    def __init__(self):
        logger.info("Initializing Pong Application")
        
        # game dimensions
        self.field_width = 800
        self.field_height = 600
        
        # initialize game
        logger.info("Creating game engine")
        self.game = PongGame(self.field_width, self.field_height)
        
        # initialize renderer
        logger.info("Creating renderer")
        self.renderer = Renderer(self.field_width, self.field_height)
        
        # Connect trail callbacks
        self.game.set_trail_callbacks(
            self.renderer.paint_trail,
            self.renderer.change_trail_color
        )
        
        # initialize wx application
        logger.info("Initializing wx application")
        self.app = wx.App()
        
        logger.info("Creating main window")
        self.frame = PongFrame(self.game, self.renderer, on_close_callback=self.on_close)
        
        # game loop control
        self.running = True
        self.last_time = time.time()
        
        # timer for game updates
        logger.info("Setting up game timer")
        timer_id = wx.NewId()
        self.timer = wx.Timer(self.frame, timer_id)
        self.frame.Bind(wx.EVT_TIMER, self.on_timer, id=timer_id)
        self.timer.Start(16)  # ~60 FPS
        
        logger.info(f"Timer started with ID {timer_id}, interval 16ms")
        logger.info("Application initialized successfully")
    
    def on_close(self):
        """Handle application close"""
        self.running = False
        self.timer.Stop()
    
    def on_timer(self, event):
        """Timer callback for game loop"""
        if not self.running:
            logger.debug("Timer fired but running=False")
            return
        
        try:
            # calculate delta time
            current_time = time.time()
            delta_time = current_time - self.last_time
            self.last_time = current_time
            
            # cap delta time to prevent large jumps
            delta_time = min(delta_time, 0.1)
            
            # Debug: log paddle direction before update
            if delta_time > 0:
                logger.debug(f"Game update: paddle_left direction={self.game.paddle_left.direction}, "
                           f"position={self.game.paddle_left.position[1]:.1f}")
            
            # update game
            self.game.update(delta_time)
            
            # render frame
            frame = self.renderer.render(self.game)
            
            if frame is None or frame.size == 0:
                logger.error("Renderer returned invalid frame")
                return
            
            # update display directly (wx.Timer already runs in main thread)
            self.frame.update_display(frame)
            
        except Exception as e:
            logger.error(f"Error in game loop: {e}", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())
    
    def run(self):
        """Start the application main loop"""
        logger.info("Starting main loop")
        
        # Initial render to show something immediately
        try:
            logger.info("Rendering initial frame...")
            frame = self.renderer.render(self.game)
            logger.info(f"Initial frame shape: {frame.shape if frame is not None else 'None'}")
            if frame is not None:
                self.frame.update_display(frame)
                logger.info("Initial frame displayed")
                self.frame.Refresh()
        except Exception as e:
            logger.error(f"Error rendering initial frame: {e}", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())
        
        logger.info(f"Timer running: {self.timer.IsRunning()}")
        
        self.app.MainLoop()
        logger.info("Main loop ended")


def main():
    """Entry point"""
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

