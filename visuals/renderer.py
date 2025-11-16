"""OpenCV-based rendering for game visualization"""

import cv2
import numpy as np
import logging

logger = logging.getLogger(__name__)


class Renderer:
    """Handles rendering of game elements using OpenCV"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.trail_enabled = False
        
        from .effects import VisualEffects
        self.effects = VisualEffects(width, height)
    
    
    def update_effects(self, delta_time):
        """Update visual effects"""
        self.effects.update(delta_time)
    
    def paint_trail(self, start_pos, end_pos):
        """Paint a trail line (disabled)"""
        pass
    
    def change_trail_color(self):
        """Change trail color (disabled)"""
        pass
    
    def clear_canvas(self):
        """Clear the canvas (disabled)"""
        pass
    
    def render(self, game):
        """Render complete game frame"""
        try:
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            
            overlay = frame.copy()
            
            for y in range(0, self.height, 20):
                cv2.line(overlay, 
                         (self.width // 2, y), 
                         (self.width // 2, min(y + 10, self.height)),
                         (128, 128, 128), 2)
            
            self._draw_paddle(overlay, game.paddle_left, (255, 255, 255))
            self._draw_paddle(overlay, game.paddle_right, (255, 255, 255))
            self._draw_ball(overlay, game.ball, (255, 255, 0))
            
            alpha = 0.8
            frame = cv2.addWeighted(frame, 1 - alpha, overlay, alpha, 0)
            
            self._draw_bounces(frame, game.bounce_count)
            
            if game.game_state == 'paused':
                self._draw_text(frame, "PAUSED", (self.width // 2 - 100, self.height // 2), 
                              color=(255, 255, 255), scale=2)
            
            frame = self.effects.apply_effects(frame)
            return frame
        except Exception as e:
            logger.error(f"Error in render: {e}", exc_info=True)
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
    
    def _draw_bounces(self, frame, bounce_count):
        """Draw score at top center"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        scale = 2.0
        thickness = 3
        color = (0, 0, 255)  # Red
        text = str(bounce_count)
        size = cv2.getTextSize(text, font, scale, thickness)[0]
        cv2.putText(frame, text,
                   (self.width // 2 - size[0] // 2, 55),
                   font, scale, color, thickness)
    
    def _draw_text(self, frame, text, position, color=(255, 255, 255), scale=1):
        """Draw text on frame"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        thickness = 2
        cv2.putText(frame, text, position, font, scale, color, thickness)
    
    def trigger_goal_flash(self, player_left=True):
        """Trigger goal flash effect"""
        self.effects.trigger_goal_flash(player_left)
    
    def trigger_collision_particles(self, x, y):
        """Trigger collision particles"""
        self.effects.trigger_collision_particles(x, y)
