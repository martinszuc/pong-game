"""AI opponent for Pong game"""

import logging

logger = logging.getLogger(__name__)


class SimpleAI:
    """Simple AI that follows the ball"""
    
    def __init__(self, paddle, difficulty=0.5):
        self.paddle = paddle
        self.difficulty = max(0.0, min(1.0, difficulty))
        self.reaction_delay = 0.05 * (1.0 - self.difficulty)
    
    def update(self, ball, delta_time):
        """Update AI paddle movement based on ball position"""
        if not ball:
            return
        
        ball_y = ball.position[1]
        paddle_center_y = self.paddle.get_center_y()
        distance = ball_y - paddle_center_y
        threshold = 15.0
        
        if abs(distance) > threshold:
            if distance > 0:
                self.paddle.move_down()
            else:
                self.paddle.move_up()
        else:
            self.paddle.stop()
