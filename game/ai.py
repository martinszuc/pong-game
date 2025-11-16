import logging

logger = logging.getLogger(__name__)

MIN_DIFFICULTY = 0.0
MAX_DIFFICULTY = 1.0
DEFAULT_DIFFICULTY = 0.5
REACTION_DELAY_BASE = 0.05
AI_THRESHOLD = 15.0


class SimpleAI:
    def __init__(self, paddle, difficulty=DEFAULT_DIFFICULTY):
        self.paddle = paddle
        self.difficulty = max(MIN_DIFFICULTY, min(MAX_DIFFICULTY, difficulty))
        self.reaction_delay = REACTION_DELAY_BASE * (1.0 - self.difficulty)
    
    def update(self, ball, delta_time):
        if not ball:
            return
        
        ball_y = ball.position[1]
        paddle_center_y = self.paddle.get_center_y()
        distance = ball_y - paddle_center_y
        
        if abs(distance) > AI_THRESHOLD:
            if distance > 0:
                self.paddle.move_down()
            else:
                self.paddle.move_up()
        else:
            self.paddle.stop()
