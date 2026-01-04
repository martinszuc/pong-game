"""
ai.py - Computer opponent AI

This file contains the "brain" that controls the right paddle (the AI opponent).
It's purposely made to be imperfect so the game is fair and fun!
"""

import logging

logger = logging.getLogger(__name__)

# difficulty range (0.0 = easiest, 1.0 = hardest)
MIN_DIFFICULTY = 0.0
MAX_DIFFICULTY = 1.0
DEFAULT_DIFFICULTY = 0.5

# base reaction delay (higher difficulty = faster reactions)
REACTION_DELAY_BASE = 0.05

# how close the paddle needs to be to the ball before it stops moving
# (if this is too small, the AI "jitters" back and forth)
AI_THRESHOLD = 15.0


class SimpleAI:
    """
    simple AI that tracks the ball
    
    the AI tries to move its paddle to where the ball is, but it's
    not perfect - the difficulty setting controls how good it is
    """
    
    def __init__(self, paddle, difficulty=DEFAULT_DIFFICULTY):
        """
        create an AI to control a paddle
        
        difficulty: 0.0 (easy) to 1.0 (hard)
        - lower difficulty = slower reactions
        - higher difficulty = faster, more accurate
        """
        self.paddle = paddle
        
        # clamp difficulty to valid range
        self.difficulty = max(MIN_DIFFICULTY, min(MAX_DIFFICULTY, difficulty))
        
        # reaction delay (easier AI = slower reactions)
        self.reaction_delay = REACTION_DELAY_BASE * (1.0 - self.difficulty)
    
    def update(self, ball, delta_time):
        """
        decide how to move the paddle this frame
        
        the AI's strategy is simple:
        - if the ball is above the paddle center, move up
        - if the ball is below the paddle center, move down
        - if the ball is close to the center, stop (prevents jittering)
        """
        if not ball:
            return
        
        # where is the ball?
        ball_y = ball.position[1]
        
        # where is the center of our paddle?
        paddle_center_y = self.paddle.get_center_y()
        
        # how far apart are they?
        distance = ball_y - paddle_center_y
        
        # if the ball is far enough away, move toward it
        if abs(distance) > AI_THRESHOLD:
            if distance > 0:  # ball is below paddle
                self.paddle.move_down()
            else:  # ball is above paddle
                self.paddle.move_up()
        else:
            # ball is close enough to center - stop moving
            self.paddle.stop()
