"""
Renderer: OpenCV-based rendering for game visualization
"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class Renderer:
    """Handles rendering of game elements using OpenCV"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.background = None  # will be webcam feed later
    
    def set_background(self, frame):
        """Set background frame (webcam feed)"""
        if frame is not None:
            self.background = cv2.resize(frame, (self.width, self.height))
    
    def render(self, game):
        """Render complete game frame"""
        try:
            # create base frame (black background, or webcam if available)
            if self.background is not None:
                frame = self.background.copy()
            else:
                # Use dark gray instead of pure black so we can see if rendering works
                frame = np.full((self.height, self.width, 3), 20, dtype=np.uint8)
            
            # create overlay for game elements
            overlay = frame.copy()
            
            # draw center line (dashed)
            for y in range(0, self.height, 20):
                cv2.line(overlay, 
                         (self.width // 2, y), 
                         (self.width // 2, min(y + 10, self.height)),
                         (128, 128, 128), 2)
            
            # draw paddles
            self._draw_paddle(overlay, game.paddle_left, (255, 255, 255))
            self._draw_paddle(overlay, game.paddle_right, (255, 255, 255))
            
            # draw ball
            self._draw_ball(overlay, game.ball, (255, 255, 0))
            
            # blend overlay with background
            alpha = 0.8  # More opaque so elements are more visible
            frame = cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)
            
            # draw score
            self._draw_score(frame, game.score_left, game.score_right)
            
            # draw game state
            if game.game_state == 'paused':
                self._draw_text(frame, "PAUSED", (self.width // 2 - 100, self.height // 2), 
                              color=(255, 255, 255), scale=2)
            
            logger.debug(f"Rendered frame: shape={frame.shape}, min={frame.min()}, max={frame.max()}")
            return frame
        except Exception as e:
            logger.error(f"Error in render: {e}", exc_info=True)
            import traceback
            logger.error(traceback.format_exc())
            # Return a test pattern on error so we can see something
            error_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(error_frame, "RENDER ERROR", (50, self.height // 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            return error_frame
    
    def _draw_paddle(self, frame, paddle, color):
        """Draw a paddle rectangle"""
        x = int(paddle.position[0])
        y = int(paddle.position[1])
        w = int(paddle.width)
        h = int(paddle.height)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
    
    def _draw_ball(self, frame, ball, color):
        """Draw the ball as a circle"""
        center = (int(ball.position[0]), int(ball.position[1]))
        radius = int(ball.radius)
        cv2.circle(frame, center, radius, color, -1)
    
    def _draw_score(self, frame, score_left, score_right):
        """Draw score text"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 2
        thickness = 3
        color = (255, 255, 255)
        
        # left score
        text_left = str(score_left)
        size_left = cv2.getTextSize(text_left, font, scale, thickness)[0]
        cv2.putText(frame, text_left, 
                   (self.width // 4 - size_left[0] // 2, 50),
                   font, scale, color, thickness)
        
        # right score
        text_right = str(score_right)
        size_right = cv2.getTextSize(text_right, font, scale, thickness)[0]
        cv2.putText(frame, text_right,
                   (3 * self.width // 4 - size_right[0] // 2, 50),
                   font, scale, color, thickness)
    
    def _draw_text(self, frame, text, position, color=(255, 255, 255), scale=1):
        """Draw text on frame"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 2
        cv2.putText(frame, text, position, font, scale, color, thickness)

