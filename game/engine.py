import logging
import random
from .entities import Ball, Paddle

logger = logging.getLogger(__name__)

PADDLE_WIDTH = 10
PADDLE_HEIGHT = 80
PADDLE_SPEED = 300
PADDLE_MARGIN = 20
BALL_RADIUS = 8
BALL_SPEED = 250
BALL_ANGLE_RANGE = (-0.5, 0.5)
PADDLE_HIT_VELOCITY_BOOST = 50
AI_DIFFICULTY = 0.6


class PongGame:
    def __init__(self, field_width, field_height):
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
        
        self._init_paddles()
        self._init_ai()
        self.reset_ball()
        self.last_ball_position = [self.ball.position[0], self.ball.position[1]]
        logger.info(f"Game initialized: {field_width}x{field_height}")
    
    def _init_paddles(self):
        paddle_y = self.field_height // 2 - PADDLE_HEIGHT // 2
        
        self.paddle_left = Paddle(
            PADDLE_MARGIN,
            paddle_y,
            PADDLE_WIDTH,
            PADDLE_HEIGHT,
            PADDLE_SPEED
        )
        
        self.paddle_right = Paddle(
            self.field_width - PADDLE_MARGIN - PADDLE_WIDTH,
            paddle_y,
            PADDLE_WIDTH,
            PADDLE_HEIGHT,
            PADDLE_SPEED
        )
    
    def _init_ai(self):
        from .ai import SimpleAI
        self.ai = SimpleAI(self.paddle_right, difficulty=AI_DIFFICULTY)
    
    def reset_ball(self):
        angle = random.uniform(*BALL_ANGLE_RANGE)
        direction = 1 if random.random() > 0.5 else -1
        
        self.ball = Ball(
            self.field_width // 2,
            self.field_height // 2,
            radius=BALL_RADIUS,
            velocity_x=BALL_SPEED * direction,
            velocity_y=BALL_SPEED * angle
        )
        self.last_ball_position = [self.ball.position[0], self.ball.position[1]]
    
    def check_collision(self, ball, paddle):
        ball_left, ball_top, ball_right, ball_bottom = ball.get_rect()
        paddle_left, paddle_top, paddle_right, paddle_bottom = paddle.get_rect()
        
        return (ball_right >= paddle_left and 
                ball_left <= paddle_right and
                ball_bottom >= paddle_top and
                ball_top <= paddle_bottom)
    
    def update(self, delta_time):
        if self.game_state != 'playing':
            self.paddle_left.stop()
            self.paddle_right.stop()
            return
        
        if self.ai:
            self.ai.update(self.ball, delta_time)
        
        self.paddle_left.update(delta_time, self.field_height)
        self.paddle_right.update(delta_time, self.field_height)
        self.ball.update(delta_time)
        
        if self.enable_trail and self.last_ball_position is not None:
            current_pos = [self.ball.position[0], self.ball.position[1]]
            self._trail_callback(self.last_ball_position, current_pos)
        
        self._handle_wall_collisions()
        self._handle_paddle_collisions()
        self._handle_goals()
        self._normalize_ball_velocity()
        
        self.last_ball_position = [self.ball.position[0], self.ball.position[1]]
    
    def _handle_wall_collisions(self):
        ball_x, ball_y = self.ball.position
        
        if ball_y - self.ball.radius <= 0 or ball_y + self.ball.radius >= self.field_height:
            self.ball.reflect_y()
            ball_y = max(self.ball.radius, min(self.field_height - self.ball.radius, ball_y))
            self.ball.position[1] = ball_y
            
            if self.enable_trail:
                self._color_change_callback()
            
            self._trigger_callbacks('wall_bounce', ball_x, ball_y)
    
    def _handle_paddle_collisions(self):
        ball_x, ball_y = self.ball.position
        paddle_hit = None
        hit_position = None
        
        if self.check_collision(self.ball, self.paddle_left):
            self._handle_paddle_hit(self.paddle_left, 'left')
            paddle_hit = 'left'
            hit_position = self._calculate_hit_position(self.paddle_left)
            self.bounce_count += 1
        
        if self.check_collision(self.ball, self.paddle_right):
            self._handle_paddle_hit(self.paddle_right, 'right')
            paddle_hit = 'right'
            hit_position = self._calculate_hit_position(self.paddle_right)
        
        if paddle_hit:
            if self.enable_trail:
                self._color_change_callback()
            
            paddle = self.paddle_left if paddle_hit == 'left' else self.paddle_right
            if 'paddle_hit' in self._audio_callbacks:
                self._audio_callbacks['paddle_hit'](hit_position, paddle.height)
            if 'paddle_hit' in self._visual_callbacks:
                self._visual_callbacks['paddle_hit'](ball_x, ball_y)
            if 'collision_flash' in self._lighting_callbacks:
                self._lighting_callbacks['collision_flash']()
    
    def _handle_paddle_hit(self, paddle, side):
        if side == 'left':
            self.ball.position[0] = paddle.position[0] + paddle.width + self.ball.radius
        else:
            self.ball.position[0] = paddle.position[0] - self.ball.radius
        
        self.ball.reflect_x()
        self.ball.increase_speed()
        hit_position = self._calculate_hit_position(paddle)
        self.ball.velocity[1] += hit_position * PADDLE_HIT_VELOCITY_BOOST
    
    def _calculate_hit_position(self, paddle):
        return (self.ball.position[1] - paddle.get_center_y()) / (paddle.height / 2)
    
    def _handle_goals(self):
        ball_x = self.ball.position[0]
        
        if ball_x < 0:
            self.game_state = 'game_over'
            self._trigger_callbacks('goal', player_left=False)
        elif ball_x > self.field_width:
            self.game_state = 'game_over'
            self._trigger_callbacks('goal', player_left=True)
    
    def _trigger_callbacks(self, event_type, *args, **kwargs):
        if event_type == 'wall_bounce':
            ball_x, ball_y = args
            if 'ball_bounce' in self._audio_callbacks:
                self._audio_callbacks['ball_bounce'](ball_y, self.field_height)
            if 'wall_bounce' in self._visual_callbacks:
                self._visual_callbacks['wall_bounce'](ball_x, ball_y)
            if 'collision_flash' in self._lighting_callbacks:
                self._lighting_callbacks['collision_flash']()
        elif event_type == 'goal':
            player_left = kwargs.get('player_left', True)
            if 'score' in self._audio_callbacks:
                self._audio_callbacks['score'](player_left=player_left)
            if 'goal_flash' in self._visual_callbacks:
                self._visual_callbacks['goal_flash'](player_left)
            if 'goal_flash' in self._lighting_callbacks:
                self._lighting_callbacks['goal_flash'](player_left)
    
    def _normalize_ball_velocity(self):
        current_speed = (self.ball.velocity[0]**2 + self.ball.velocity[1]**2)**0.5
        if current_speed > 0:
            speed_factor = self.ball.speed / current_speed
            self.ball.velocity[0] *= speed_factor
            self.ball.velocity[1] *= speed_factor
    
    def pause(self):
        if self.game_state == 'playing':
            self.game_state = 'paused'
        elif self.game_state == 'paused':
            self.game_state = 'playing'
    
    def start_game(self):
        if self.game_state == 'menu':
            self.game_state = 'playing'
            self.reset_game()
    
    def to_menu(self):
        self.game_state = 'menu'
    
    def reset_game(self):
        self.score_left = 0
        self.score_right = 0
        self.bounce_count = 0
        self.game_state = 'playing'
        self.reset_ball()
    
    def set_trail_callbacks(self, trail_callback, color_change_callback):
        self._trail_callback = trail_callback
        self._color_change_callback = color_change_callback
    
    def set_audio_callbacks(self, **callbacks):
        self._audio_callbacks.update(callbacks)
    
    def set_visual_callbacks(self, **callbacks):
        self._visual_callbacks.update(callbacks)
    
    def set_lighting_callbacks(self, **callbacks):
        self._lighting_callbacks.update(callbacks)
