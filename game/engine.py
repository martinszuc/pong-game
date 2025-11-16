"""Game engine: physics, collision detection, and game state management"""

import logging
from .entities import Ball, Paddle

logger = logging.getLogger(__name__)


class PongGame:
    """Main game logic and state management"""
    
    def __init__(self, field_width, field_height, ai_enabled=True):
        self.field_width = field_width
        self.field_height = field_height
        self.score_left = 0
        self.score_right = 0
        self.game_state = 'menu'
        self.last_ball_position = None
        self.enable_trail = False
        self.bounce_count = 0
        
        self._audio_callbacks = {}
        self._visual_callbacks = {}
        self._lighting_callbacks = {}
        
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
        
        self.ai_enabled = ai_enabled
        if ai_enabled:
            from .ai import SimpleAI
            self.ai = SimpleAI(self.paddle_right, difficulty=0.6)
        else:
            self.ai = None
        
        self.reset_ball()
        self.last_ball_position = [self.ball.position[0], self.ball.position[1]]
        logger.info(f"Game initialized: {field_width}x{field_height}")
    
    def reset_ball(self):
        """Reset ball to center with random initial direction"""
        import random
        ball_speed = 250
        angle = random.uniform(-0.5, 0.5)
        
        self.ball = Ball(
            self.field_width // 2,
            self.field_height // 2,
            radius=8,
            velocity_x=ball_speed * (1 if random.random() > 0.5 else -1),
            velocity_y=ball_speed * angle
        )
        self.last_ball_position = [self.ball.position[0], self.ball.position[1]]
    
    def check_collision(self, ball, paddle):
        """Check if ball collides with paddle"""
        ball_left, ball_top, ball_right, ball_bottom = ball.get_rect()
        paddle_left, paddle_top, paddle_right, paddle_bottom = paddle.get_rect()
        
        return (ball_right >= paddle_left and 
                ball_left <= paddle_right and
                ball_bottom >= paddle_top and
                ball_top <= paddle_bottom)
    
    def update(self, delta_time):
        """Update game state"""
        if self.ai_enabled and self.ai and self.game_state == 'playing':
            self.ai.update(self.ball, delta_time)
        
        self.paddle_left.update(delta_time, self.field_height)
        self.paddle_right.update(delta_time, self.field_height)
        
        if self.game_state != 'playing':
            return
        
        self.ball.update(delta_time)
        
        if self.enable_trail and self.last_ball_position is not None:
            current_pos = [self.ball.position[0], self.ball.position[1]]
            self._trail_callback(self.last_ball_position, current_pos)
        
        ball_x, ball_y = self.ball.position
        bounced = False
        
        if ball_y - self.ball.radius <= 0 or ball_y + self.ball.radius >= self.field_height:
            self.ball.reflect_y()
            bounced = True
            ball_y = max(self.ball.radius, min(self.field_height - self.ball.radius, ball_y))
            self.ball.position[1] = ball_y
        
        self.last_ball_position = [self.ball.position[0], self.ball.position[1]]
        
        if bounced and self.enable_trail:
            self._color_change_callback()
        
        if bounced:
            if 'ball_bounce' in self._audio_callbacks:
                self._audio_callbacks['ball_bounce'](ball_y, self.field_height)
            if 'wall_bounce' in self._visual_callbacks:
                self._visual_callbacks['wall_bounce'](ball_x, ball_y)
            if 'collision_flash' in self._lighting_callbacks:
                self._lighting_callbacks['collision_flash']()
        
        bounced = False
        paddle_hit = None
        hit_position = None
        
        if self.check_collision(self.ball, self.paddle_left):
            self.ball.position[0] = self.paddle_left.position[0] + self.paddle_left.width + self.ball.radius
            self.ball.reflect_x()
            self.ball.increase_speed()
            bounced = True
            paddle_hit = 'left'
            hit_position = (self.ball.position[1] - self.paddle_left.get_center_y()) / (self.paddle_left.height / 2)
            self.ball.velocity[1] += hit_position * 50
            self.bounce_count += 1

        if self.check_collision(self.ball, self.paddle_right):
            self.ball.position[0] = self.paddle_right.position[0] - self.ball.radius
            self.ball.reflect_x()
            self.ball.increase_speed()
            bounced = True
            paddle_hit = 'right'
            hit_position = (self.ball.position[1] - self.paddle_right.get_center_y()) / (self.paddle_right.height / 2)
            self.ball.velocity[1] += hit_position * 50

        if bounced and self.enable_trail:
            self._color_change_callback()
        
        if bounced:
            if 'paddle_hit' in self._audio_callbacks:
                paddle = self.paddle_left if paddle_hit == 'left' else self.paddle_right
                self._audio_callbacks['paddle_hit'](hit_position, paddle.height)
            if 'paddle_hit' in self._visual_callbacks:
                self._visual_callbacks['paddle_hit'](ball_x, ball_y)
            if 'collision_flash' in self._lighting_callbacks:
                self._lighting_callbacks['collision_flash']()
        
        if ball_x < 0:
            self.game_state = 'game_over'
            if 'score' in self._audio_callbacks:
                self._audio_callbacks['score'](player_left=False)
            if 'goal_flash' in self._visual_callbacks:
                self._visual_callbacks['goal_flash'](player_left=False)
            if 'goal_flash' in self._lighting_callbacks:
                self._lighting_callbacks['goal_flash'](player_left=False)
        elif ball_x > self.field_width:
            self.game_state = 'game_over'
            if 'score' in self._audio_callbacks:
                self._audio_callbacks['score'](player_left=True)
            if 'goal_flash' in self._visual_callbacks:
                self._visual_callbacks['goal_flash'](player_left=True)
            if 'goal_flash' in self._lighting_callbacks:
                self._lighting_callbacks['goal_flash'](player_left=True)
        
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
    
    def start_game(self):
        """Start the game from menu"""
        if self.game_state == 'menu':
            self.game_state = 'playing'
            self.reset_game()
    
    def to_menu(self):
        """Return to menu"""
        self.game_state = 'menu'
    
    def reset_game(self):
        """Reset game to initial state"""
        self.score_left = 0
        self.score_right = 0
        self.bounce_count = 0
        self.game_state = 'playing'
        self.reset_ball()
    
    def set_trail_callbacks(self, trail_callback, color_change_callback):
        """Set callbacks for trail painting and color changes"""
        self._trail_callback = trail_callback
        self._color_change_callback = color_change_callback
    
    def set_audio_callbacks(self, **callbacks):
        """Set audio event callbacks"""
        self._audio_callbacks.update(callbacks)
    
    def set_visual_callbacks(self, **callbacks):
        """Set visual event callbacks"""
        self._visual_callbacks.update(callbacks)
    
    def set_lighting_callbacks(self, **callbacks):
        """Set lighting event callbacks"""
        self._lighting_callbacks.update(callbacks)
