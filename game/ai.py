"""
AI opponent for Pong game
"""

import logging

logger = logging.getLogger(__name__)


class SimpleAI:
    """Simple AI that follows the ball"""
    
    def __init__(self, paddle, difficulty=0.5):
        """
        Args:
            paddle: Paddle instance to control
            difficulty: 0.0 (easy) to 1.0 (hard), affects reaction speed
        """
        self.paddle = paddle
        self.difficulty = max(0.0, min(1.0, difficulty))
        self.reaction_delay = 0.05 * (1.0 - self.difficulty)  # delay in seconds
    
    def update(self, ball, delta_time):
        """Update AI paddle movement based on ball position"""
        if not ball:
            return
        
        ball_y = ball.position[1]
        paddle_center_y = self.paddle.get_center_y()
        
        # calculate distance
        distance = ball_y - paddle_center_y
        
        # threshold to avoid jittery movement
        threshold = 15.0
        
        # Move toward ball if distance is significant
        if abs(distance) > threshold:
            if distance > 0:
                # Ball is below paddle center, move down
                self.paddle.move_down()
            else:
                # Ball is above paddle center, move up
                self.paddle.move_up()
        else:
            # Stop when close enough
            self.paddle.stop()

