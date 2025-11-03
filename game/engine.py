"""
Game engine: physics, collision detection, and game state management
"""

import logging
from .entities import Ball, Paddle

logger = logging.getLogger(__name__)


class PongGame:
    """Main game logic and state management"""
    
    def __init__(self, field_width, field_height, ai_enabled=True):
        self.field_width = field_width
        self.field_height = field_height
        
        logger.info(f"Initializing game with field size: {field_width}x{field_height}")
        
        # game state
        self.score_left = 0
        self.score_right = 0
        self.game_state = 'playing'  # 'playing', 'paused', 'game_over'
        
        # initialize paddles
        paddle_width = 10
        paddle_height = 80
        paddle_speed = 300
        paddle_margin = 20
        
        self.paddle_left = Paddle(
            paddle_margin,
            field_height // 2 - paddle_height // 2,
            paddle_width,
            paddle_height,
            paddle_speed
        )
        
        self.paddle_right = Paddle(
            field_width - paddle_margin - paddle_width,
            field_height // 2 - paddle_height // 2,
            paddle_width,
            paddle_height,
            paddle_speed
        )
        
        # AI opponent
        self.ai_enabled = ai_enabled
        if ai_enabled:
            from .ai import SimpleAI
            self.ai = SimpleAI(self.paddle_right, difficulty=0.6)
            logger.info("AI opponent enabled")
        else:
            self.ai = None
        
        # initialize ball
        self.reset_ball()
        logger.info("Game initialized successfully")
    
    def reset_ball(self):
        """Reset ball to center with random initial direction"""
        import random
        ball_speed = 250
        angle = random.uniform(-0.5, 0.5)  # random angle between -30 and 30 degrees
        
        self.ball = Ball(
            self.field_width // 2,
            self.field_height // 2,
            radius=8,
            velocity_x=ball_speed * (1 if random.random() > 0.5 else -1),
            velocity_y=ball_speed * angle
        )
    
    def check_collision(self, ball, paddle):
        """Check if ball collides with paddle"""
        ball_left, ball_top, ball_right, ball_bottom = ball.get_rect()
        paddle_left, paddle_top, paddle_right, paddle_bottom = paddle.get_rect()
        
        return (ball_right >= paddle_left and 
                ball_left <= paddle_right and
                ball_bottom >= paddle_top and
                ball_top <= paddle_bottom)
    
    def update(self, delta_time):
        """Update game state (physics, collisions, scoring)"""
        if self.game_state != 'playing':
            return
        
        # update AI if enabled (must be before paddle update)
        if self.ai_enabled and self.ai:
            self.ai.update(self.ball, delta_time)
        
        # update paddles (this applies the direction set by AI or keyboard)
        self.paddle_left.update(delta_time, self.field_height)
        self.paddle_right.update(delta_time, self.field_height)
        
        # update ball
        self.ball.update(delta_time)
        
        # ball-wall collisions (top/bottom)
        ball_x, ball_y = self.ball.position
        if ball_y - self.ball.radius <= 0 or ball_y + self.ball.radius >= self.field_height:
            self.ball.reflect_y()
            # keep ball in bounds
            ball_y = max(self.ball.radius, min(self.field_height - self.ball.radius, ball_y))
            self.ball.position[1] = ball_y
        
        # ball-paddle collisions
        if self.check_collision(self.ball, self.paddle_left):
            self.ball.position[0] = self.paddle_left.position[0] + self.paddle_left.width + self.ball.radius
            self.ball.reflect_x()
            # add slight angle based on where ball hit paddle
            hit_position = (self.ball.position[1] - self.paddle_left.get_center_y()) / (self.paddle_left.height / 2)
            self.ball.velocity[1] += hit_position * 50
        
        if self.check_collision(self.ball, self.paddle_right):
            self.ball.position[0] = self.paddle_right.position[0] - self.ball.radius
            self.ball.reflect_x()
            # add slight angle based on where ball hit paddle
            hit_position = (self.ball.position[1] - self.paddle_right.get_center_y()) / (self.paddle_right.height / 2)
            self.ball.velocity[1] += hit_position * 50
        
        # scoring (ball out of bounds)
        if ball_x < 0:
            self.score_right += 1
            self.reset_ball()
        elif ball_x > self.field_width:
            self.score_left += 1
            self.reset_ball()
        
        # normalize ball velocity to maintain consistent speed
        current_speed = (self.ball.velocity[0]**2 + self.ball.velocity[1]**2)**0.5
        if current_speed > 0:
            speed_factor = self.ball.speed / current_speed
            self.ball.velocity[0] *= speed_factor
            self.ball.velocity[1] *= speed_factor
    
    def pause(self):
        """Toggle pause state"""
        if self.game_state == 'playing':
            self.game_state = 'paused'
        elif self.game_state == 'paused':
            self.game_state = 'playing'
    
    def reset_game(self):
        """Reset game to initial state"""
        self.score_left = 0
        self.score_right = 0
        self.game_state = 'playing'
        self.reset_ball()

