"""
renderer.py - Visual rendering (drawing the game)

This file is responsible for drawing everything you see on screen:
- the paddles and ball
- the center line
- the score
- visual effects (flashes, particles)

It uses OpenCV (cv2) to draw graphics and numpy for image manipulation.
"""

import cv2  # OpenCV - computer vision and graphics library
import numpy as np  # numpy - numerical computing (used for image arrays)
import logging

from .effects import VisualEffects
from .themes import get_theme, THEMES

logger = logging.getLogger(__name__)

# center line appearance (the dashed line down the middle)
CENTER_LINE_SPACING = 20  # space between dashes
CENTER_LINE_SEGMENT = 10  # length of each dash

# how transparent the overlay should be (0.0 = invisible, 1.0 = opaque)
OVERLAY_ALPHA = 0.8

# score display settings
SCORE_FONT_SCALE = 2.0  # how big the score text is
SCORE_THICKNESS = 3  # how thick the score text is
SCORE_Y_OFFSET = 55  # how far from the top to draw the score

# "PAUSED" text positioning
PAUSED_TEXT_X_OFFSET = 100

# general text thickness
TEXT_THICKNESS = 2


class Renderer:
    """
    the renderer - draws everything on screen
    
    this class creates the visual output for the game. it draws:
    - the game field and center line
    - both paddles
    - the ball
    - the score
    - visual effects (flashes, particles, etc.)
    """
    
    def __init__(self, width, height, theme_name='classic'):
        """create a renderer for the given screen size"""
        self.width = width
        self.height = height
        self.trail_enabled = False  # ball trail effect (not currently used)
        self.effects = VisualEffects(width, height)  # particle effects system
        self.theme = get_theme(theme_name)  # current color theme
        self.theme_name = theme_name
    
    def update_effects(self, delta_time):
        """update animated effects (fade out flashes, move particles, etc.)"""
        self.effects.update(delta_time)
    
    def paint_trail(self, start_pos, end_pos):
        """draw a trail behind the ball (not currently implemented)"""
        pass
    
    def change_trail_color(self):
        """change the trail color (not currently implemented)"""
        pass
    
    def clear_canvas(self):
        """clear the drawing canvas (not currently used)"""
        pass
    
    def set_theme(self, theme_name):
        """
        change the color theme
        updates all colors used for drawing
        """
        self.theme = get_theme(theme_name)
        self.theme_name = theme_name
        logger.info(f"Theme changed to: {theme_name}")
    
    def render(self, game):
        """
        draw the entire game frame
        
        this creates one complete image of the game. steps:
        1. create a black background
        2. draw the center line
        3. draw the paddles and ball
        4. draw the score
        5. apply visual effects (flashes, particles)
        6. return the final image
        
        returns: a numpy array (the image) that can be displayed on screen
        """
        try:
            # create background with theme tint
            bg_color = self.theme['bg_tint']
            frame = np.full((self.height, self.width, 3), bg_color, dtype=np.uint8)
            
            # create an overlay layer for drawing (allows transparency effects)
            overlay = frame.copy()
            
            # draw the center line (dashed line down the middle)
            for y in range(0, self.height, CENTER_LINE_SPACING):
                cv2.line(overlay, 
                         (self.width // 2, y),  # start point
                         (self.width // 2, min(y + CENTER_LINE_SEGMENT, self.height)),  # end point
                         self.theme['center_line'],  # theme color
                         2)  # line thickness
            
            # draw the paddles using theme colors
            self._draw_paddle(overlay, game.paddle_left, self.theme['paddle'])
            self._draw_paddle(overlay, game.paddle_right, self.theme['paddle'])
            
            # draw the ball using theme color
            self._draw_ball(overlay, game.ball, self.theme['ball'])
            
            # blend the overlay with the background (creates transparency effect)
            frame = cv2.addWeighted(frame, 1 - OVERLAY_ALPHA, overlay, OVERLAY_ALPHA, 0)
            
            # draw the score (bounce count) at the top
            self._draw_bounces(frame, game.bounce_count)
            
            # if paused, show "PAUSED" text
            if game.game_state == 'paused':
                self._draw_text(frame, "PAUSED", 
                              (self.width // 2 - PAUSED_TEXT_X_OFFSET, self.height // 2), 
                              color=(255, 255, 255), scale=2)
            
            # apply visual effects (goal flashes, collision particles, etc.)
            frame = self.effects.apply_effects(frame)
            
            return frame
        
        except Exception as e:
            # if something goes wrong, show an error message instead of crashing
            logger.error(f"Error in render: {e}", exc_info=True)
            error_frame = np.zeros((self.height, self.width, 3), dtype=np.uint8)
            cv2.putText(error_frame, "RENDER ERROR", (50, self.height // 2), 
                       cv2.FONT_HERSHEY_SIMPLEX, 1, (255, 0, 0), 2)
            return error_frame
    
    def _draw_paddle(self, frame, paddle, color):
        """
        draw a paddle (rectangle) on the frame
        -1 means "filled" (not just an outline)
        """
        x = int(paddle.position[0])
        y = int(paddle.position[1])
        w = int(paddle.width)
        h = int(paddle.height)
        cv2.rectangle(frame, (x, y), (x + w, y + h), color, -1)
    
    def _draw_ball(self, frame, ball, color):
        """
        draw the ball (circle) on the frame
        -1 means "filled" (not just an outline)
        """
        center = (int(ball.position[0]), int(ball.position[1]))
        radius = int(ball.radius)
        cv2.circle(frame, center, radius, color, -1)
    
    def _draw_bounces(self, frame, bounce_count):
        """
        draw the bounce count (score) at the top center of the screen
        the text is centered by calculating its width
        """
        font = cv2.FONT_HERSHEY_SIMPLEX
        color = self.theme['score']  # use theme color
        text = str(bounce_count)
        
        # calculate text size so we can center it
        size = cv2.getTextSize(text, font, SCORE_FONT_SCALE, SCORE_THICKNESS)[0]
        
        # draw centered at the top
        cv2.putText(frame, text,
                   (self.width // 2 - size[0] // 2, SCORE_Y_OFFSET),
                   font, SCORE_FONT_SCALE, color, SCORE_THICKNESS)
    
    def _draw_text(self, frame, text, position, color=(255, 255, 255), scale=1):
        """draw text on the frame (used for "PAUSED" message, etc.)"""
        font = cv2.FONT_HERSHEY_SIMPLEX
        cv2.putText(frame, text, position, font, scale, color, TEXT_THICKNESS)
    
    def trigger_goal_flash(self, player_left=True):
        """trigger a screen flash when someone scores"""
        self.effects.trigger_goal_flash(player_left)
    
    def trigger_collision_particles(self, x, y):
        """trigger particle effect when ball hits something"""
        self.effects.trigger_collision_particles(x, y)
