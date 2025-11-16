import cv2
import numpy as np
import logging

from .effects import VisualEffects

logger = logging.getLogger(__name__)

CENTER_LINE_SPACING = 20
CENTER_LINE_SEGMENT = 10
OVERLAY_ALPHA = 0.8
SCORE_FONT_SCALE = 2.0
SCORE_THICKNESS = 3
SCORE_Y_OFFSET = 55
PAUSED_TEXT_X_OFFSET = 100
TEXT_THICKNESS = 2


class Renderer:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.trail_enabled = False
        self.effects = VisualEffects(width, height)
    
    def update_effects(self, delta_time):
        self.effects.update(delta_time)
    
    def paint_trail(self, start_pos, end_pos):
        pass
    
    def change_trail_color(self):
        pass
    
    def clear_canvas(self):
        pass
    
    def render(self, game):
        try:
            frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            overlay = frame.copy()
            
            for y in range(0, self.height, CENTER_LINE_SPACING):
                cv2.line(overlay, 
                         (self.width // 2, y), 
                         (self.width // 2, min(y + CENTER_LINE_SEGMENT, self.height)),
                         (128, 128, 128), 2)
            
            self._draw_paddle(overlay, game.paddle_left, (255, 255, 255))
            self._draw_paddle(overlay, game.paddle_right, (255, 255, 255))
            self._draw_ball(overlay, game.ball, (255, 255, 0))
            
            frame = cv2.addWeighted(frame, 1 - OVERLAY_ALPHA, overlay, OVERLAY_ALPHA, 0)
            
            self._draw_bounces(frame, game.bounce_count)
            
            if game.game_state == 'paused':
                self._draw_text(frame, "PAUSED", 
                              (self.width // 2 - PAUSED_TEXT_X_OFFSET, self.height // 2), 
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
        x = int(paddle.position[0])
        y = int(paddle.position[1])
        w = int(paddle.width)
        h = int(paddle.height)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
    
    def _draw_ball(self, frame, ball, color):
        center = (int(ball.position[0]), int(ball.position[1]))
        radius = int(ball.radius)
        cv2.circle(frame, center, radius, color, -1)
    
    def _draw_bounces(self, frame, bounce_count):
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = (0, 0, 255)
        text = str(bounce_count)
        size = cv2.getTextSize(text, font, SCORE_FONT_SCALE, SCORE_THICKNESS)[0]
        cv2.putText(frame, text,
                   (self.width // 2 - size[0] // 2, SCORE_Y_OFFSET),
                   font, SCORE_FONT_SCALE, color, SCORE_THICKNESS)
    
    def _draw_text(self, frame, text, position, color=(255, 255, 255), scale=1):
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, text, position, font, scale, color, TEXT_THICKNESS)
    
    def trigger_goal_flash(self, player_left=True):
        self.effects.trigger_goal_flash(player_left)
    
    def trigger_collision_particles(self, x, y):
        self.effects.trigger_collision_particles(x, y)
