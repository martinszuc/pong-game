"""
engine.py - The game engine (the "brain" of the game)

This file contains the main game logic. It handles:
- Moving the ball and paddles
- Detecting collisions (when the ball hits paddles or walls)
- Keeping track of the score
- Controlling the AI opponent
"""

import logging
import random
from .entities import Ball, Paddle

logger = logging.getLogger(__name__)

# paddle dimensions and behavior
PADDLE_WIDTH = 10  # pixels wide
PADDLE_HEIGHT = 80  # pixels tall
PADDLE_SPEED = 300  # pixels per second
PADDLE_MARGIN = 20  # distance from edge of screen

# ball properties
BALL_RADIUS = 8  # pixels
BALL_SPEED = 250  # pixels per second

# ball angle when it spawns (keeps it from going straight horizontal)
BALL_ANGLE_RANGE = (-0.5, 0.5)

# how much the paddle's movement affects the ball's angle
PADDLE_HIT_VELOCITY_BOOST = 50

# AI difficulty (0.0 = terrible, 1.0 = perfect)
AI_DIFFICULTY = 0.6

# difficulty presets - adjust multiple parameters at once
DIFFICULTY_PRESETS = {
    'easy': {
        'name': 'Easy',
        'ai_difficulty': 0.1,
        'ball_speed': 200,
        'paddle_speed': 350,
        'speed_increase': 1.03,
        'max_speed_mult': 2.0
    },
    'medium': {
        'name': 'Medium',
        'ai_difficulty': 0.6,
        'ball_speed': 250,
        'paddle_speed': 300,
        'speed_increase': 1.05,
        'max_speed_mult': 2.5
    },
    'hard': {
        'name': 'Hard',
        'ai_difficulty': 0.85,
        'ball_speed': 320,
        'paddle_speed': 270,
        'speed_increase': 1.08,
        'max_speed_mult': 3.0
    }
}


class PongGame:
    """
    the main game engine
    
    this class manages everything that happens in the game:
    - the ball, paddles, and AI
    - collision detection
    - scoring
    - game states (menu, playing, paused, game over)
    """
    
    def __init__(self, field_width, field_height, difficulty='medium'):
        """initialize a new game with the given field dimensions"""
        # game field size
        self.field_width = field_width
        self.field_height = field_height
        
        # difficulty settings
        self.difficulty = difficulty
        self.apply_difficulty_preset(difficulty)
        
        # scores for both players
        self.score_left = 0
        self.score_right = 0
        
        # game state: 'menu', 'playing', 'paused', or 'game_over'
        self.game_state = 'menu'
        
        # for drawing the ball trail effect
        self.last_ball_position = None
        self.enable_trail = False
        
        # count how many times the ball has bounced (for scoring)
        self.bounce_count = 0
        
        # callback functions that trigger sounds, visuals, and lights
        self._audio_callbacks = {}
        self._visual_callbacks = {}
        self._lighting_callbacks = {}
        
        # create the game objects
        self._init_paddles()
        self._init_ai()
        self.reset_ball()
        self.last_ball_position = [self.ball.position[0], self.ball.position[1]]
        
        logger.info(f"Game initialized: {field_width}x{field_height}, difficulty: {difficulty}")
    
    def _init_paddles(self):
        """create the left and right paddles"""
        # center the paddles vertically
        paddle_y = self.field_height // 2 - PADDLE_HEIGHT // 2
        
        # left paddle (controlled by player via microphone)
        self.paddle_left = Paddle(
            PADDLE_MARGIN,  # x position (left side)
            paddle_y,  # y position (centered)
            PADDLE_WIDTH,
            PADDLE_HEIGHT,
            self.paddle_speed  # use difficulty-adjusted speed
        )
        
        # right paddle (controlled by AI)
        self.paddle_right = Paddle(
            self.field_width - PADDLE_MARGIN - PADDLE_WIDTH,  # x position (right side)
            paddle_y,  # y position (centered)
            PADDLE_WIDTH,
            PADDLE_HEIGHT,
            self.paddle_speed  # use difficulty-adjusted speed
        )
    
    def _init_ai(self):
        """create the AI that controls the right paddle"""
        from .ai import SimpleAI
        self.ai = SimpleAI(self.paddle_right, difficulty=self.ai_difficulty)
    
    def apply_difficulty_preset(self, difficulty):
        """
        apply a difficulty preset
        
        this adjusts multiple game parameters at once:
        - AI skill level
        - ball speed
        - paddle speed
        - how fast the ball speeds up
        """
        preset = DIFFICULTY_PRESETS.get(difficulty, DIFFICULTY_PRESETS['medium'])
        
        self.ai_difficulty = preset['ai_difficulty']
        self.ball_speed = preset['ball_speed']
        self.paddle_speed = preset['paddle_speed']
        self.speed_increase_factor = preset['speed_increase']
        self.max_speed_multiplier = preset['max_speed_mult']
        
        logger.info(f"Applied difficulty preset: {preset['name']}")
    
    def reset_ball(self):
        """
        create a new ball in the center of the screen
        the ball starts moving at a random angle toward a random side
        """
        # random vertical angle (so it's not perfectly horizontal)
        angle = random.uniform(*BALL_ANGLE_RANGE)
        
        # randomly choose left (-1) or right (1)
        direction = 1 if random.random() > 0.5 else -1
        
        # create the ball in the center
        self.ball = Ball(
            self.field_width // 2,  # center x
            self.field_height // 2,  # center y
            radius=BALL_RADIUS,
            velocity_x=self.ball_speed * direction,  # horizontal speed (left or right)
            velocity_y=self.ball_speed * angle,  # vertical speed (angled)
            speed_increase_factor=self.speed_increase_factor,
            max_speed_multiplier=self.max_speed_multiplier
        )
        self.last_ball_position = [self.ball.position[0], self.ball.position[1]]
    
    def check_collision(self, ball, paddle):
        """
        check if the ball and paddle are touching (collision detection)
        
        this uses "axis-aligned bounding box" collision detection:
        we check if the rectangles overlap on both x and y axes
        """
        # get the bounding boxes (left, top, right, bottom edges)
        ball_left, ball_top, ball_right, ball_bottom = ball.get_rect()
        paddle_left, paddle_top, paddle_right, paddle_bottom = paddle.get_rect()
        
        # check if they overlap on both axes
        return (ball_right >= paddle_left and  # ball's right edge is past paddle's left edge
                ball_left <= paddle_right and  # ball's left edge is before paddle's right edge
                ball_bottom >= paddle_top and  # ball's bottom is past paddle's top
                ball_top <= paddle_bottom)  # ball's top is before paddle's bottom
    
    def update(self, delta_time):
        """
        update the game for one frame
        
        this is called 60 times per second and handles:
        - moving everything
        - checking for collisions
        - updating scores
        
        delta_time: how much time has passed since last frame (in seconds)
        """
        # don't update anything if we're not playing
        if self.game_state != 'playing':
            self.paddle_left.stop()
            self.paddle_right.stop()
            return
        
        # let the AI decide how to move the right paddle
        if self.ai:
            self.ai.update(self.ball, delta_time)
        
        # move the paddles based on their direction
        self.paddle_left.update(delta_time, self.field_height)
        self.paddle_right.update(delta_time, self.field_height)
        
        # move the ball
        self.ball.update(delta_time)
        
        # draw the ball trail effect (if enabled)
        if self.enable_trail and self.last_ball_position is not None:
            current_pos = [self.ball.position[0], self.ball.position[1]]
            self._trail_callback(self.last_ball_position, current_pos)
        
        # check for collisions and goals
        self._handle_wall_collisions()
        self._handle_paddle_collisions()
        self._handle_goals()
        
        # keep the ball speed consistent (normalize the velocity vector)
        self._normalize_ball_velocity()
        
        # remember where the ball is for next frame's trail
        self.last_ball_position = [self.ball.position[0], self.ball.position[1]]
    
    def _handle_wall_collisions(self):
        """
        check if the ball hit the top or bottom wall
        if it did, bounce it back and trigger effects
        """
        ball_x, ball_y = self.ball.position
        
        # check if ball hit top wall (y <= 0) or bottom wall (y >= field_height)
        if ball_y - self.ball.radius <= 0 or ball_y + self.ball.radius >= self.field_height:
            # bounce the ball vertically
            self.ball.reflect_y()
            
            # make sure the ball stays within bounds (prevents getting stuck in walls)
            ball_y = max(self.ball.radius, min(self.field_height - self.ball.radius, ball_y))
            self.ball.position[1] = ball_y
            
            # change the trail color when the ball bounces
            if self.enable_trail:
                self._color_change_callback()
            
            # trigger sound, visual, and lighting effects
            self._trigger_callbacks('wall_bounce', ball_x, ball_y)
    
    def _handle_paddle_collisions(self):
        """
        check if the ball hit either paddle
        if it did, bounce it back and apply spin based on where it hit
        """
        ball_x, ball_y = self.ball.position
        paddle_hit = None
        hit_position = None
        
        # check left paddle (player)
        if self.check_collision(self.ball, self.paddle_left):
            self._handle_paddle_hit(self.paddle_left, 'left')
            paddle_hit = 'left'
            hit_position = self._calculate_hit_position(self.paddle_left)
            self.bounce_count += 1  # count bounces for scoring
        
        # check right paddle (AI)
        if self.check_collision(self.ball, self.paddle_right):
            self._handle_paddle_hit(self.paddle_right, 'right')
            paddle_hit = 'right'
            hit_position = self._calculate_hit_position(self.paddle_right)
        
        # if we hit a paddle, trigger effects
        if paddle_hit:
            # change trail color
            if self.enable_trail:
                self._color_change_callback()
            
            # trigger sound, visual, and lighting effects
            paddle = self.paddle_left if paddle_hit == 'left' else self.paddle_right
            if 'paddle_hit' in self._audio_callbacks:
                self._audio_callbacks['paddle_hit'](hit_position, paddle.height)
            if 'paddle_hit' in self._visual_callbacks:
                self._visual_callbacks['paddle_hit'](ball_x, ball_y)
            if 'collision_flash' in self._lighting_callbacks:
                self._lighting_callbacks['collision_flash']()
    
    def _handle_paddle_hit(self, paddle, side):
        """
        when the ball hits a paddle:
        1. move it slightly away from the paddle (prevents getting stuck)
        2. reverse horizontal direction
        3. speed up the ball
        4. apply "spin" based on where the paddle was hit
        """
        # move ball away from paddle (prevents double-collision)
        if side == 'left':
            self.ball.position[0] = paddle.position[0] + paddle.width + self.ball.radius
        else:
            self.ball.position[0] = paddle.position[0] - self.ball.radius
        
        # bounce horizontally and speed up
        self.ball.reflect_x()
        self.ball.increase_speed()
        
        # apply spin based on where the ball hit the paddle
        # hitting near the top/bottom makes the ball go up/down more
        hit_position = self._calculate_hit_position(paddle)
        self.ball.velocity[1] += hit_position * PADDLE_HIT_VELOCITY_BOOST
    
    def _calculate_hit_position(self, paddle):
        """
        calculate where on the paddle the ball hit
        returns -1.0 (top) to 1.0 (bottom), with 0.0 being the center
        """
        return (self.ball.position[1] - paddle.get_center_y()) / (paddle.height / 2)
    
    def _handle_goals(self):
        """
        check if the ball went past a paddle (someone scored)
        """
        ball_x = self.ball.position[0]
        
        # ball went past left paddle (player missed) - AI wins
        if ball_x < 0:
            self.game_state = 'game_over'
            self._trigger_callbacks('goal', player_left=False)
        
        # ball went past right paddle (AI missed) - player wins
        elif ball_x > self.field_width:
            self.game_state = 'game_over'
            self._trigger_callbacks('goal', player_left=True)
    
    def _trigger_callbacks(self, event_type, *args, **kwargs):
        """
        trigger sound, visual, and lighting effects for game events
        
        this is like the game's "event system" - when something happens
        (ball bounces, someone scores), we notify all the systems that
        want to react to it (audio, visuals, lights)
        """
        if event_type == 'wall_bounce':
            # ball bounced off a wall
            ball_x, ball_y = args
            if 'ball_bounce' in self._audio_callbacks:
                self._audio_callbacks['ball_bounce'](ball_y, self.field_height)
            if 'wall_bounce' in self._visual_callbacks:
                self._visual_callbacks['wall_bounce'](ball_x, ball_y)
            if 'collision_flash' in self._lighting_callbacks:
                self._lighting_callbacks['collision_flash']()
        
        elif event_type == 'goal':
            # someone scored
            player_left = kwargs.get('player_left', True)
            if 'score' in self._audio_callbacks:
                self._audio_callbacks['score'](player_left=player_left)
            if 'goal_flash' in self._visual_callbacks:
                self._visual_callbacks['goal_flash'](player_left)
            if 'goal_flash' in self._lighting_callbacks:
                self._lighting_callbacks['goal_flash'](player_left)
    
    def _normalize_ball_velocity(self):
        """
        keep the ball speed consistent
        
        after applying spin and bounces, the ball's velocity vector can get
        longer or shorter. this normalizes it back to the correct speed.
        uses pythagorean theorem: speed = sqrt(vx² + vy²)
        """
        current_speed = (self.ball.velocity[0]**2 + self.ball.velocity[1]**2)**0.5
        if current_speed > 0:
            speed_factor = self.ball.speed / current_speed
            self.ball.velocity[0] *= speed_factor
            self.ball.velocity[1] *= speed_factor
    
    def pause(self):
        """toggle pause state (playing <-> paused)"""
        if self.game_state == 'playing':
            self.game_state = 'paused'
        elif self.game_state == 'paused':
            self.game_state = 'playing'
    
    def start_game(self):
        """start a new game from the menu"""
        if self.game_state == 'menu':
            self.game_state = 'playing'
            self.reset_game()
    
    def to_menu(self):
        """return to the main menu"""
        self.game_state = 'menu'
    
    def reset_game(self):
        """reset all game state for a new game"""
        self.score_left = 0
        self.score_right = 0
        self.bounce_count = 0
        self.game_state = 'playing'
        self.reset_ball()
    
    def set_trail_callbacks(self, trail_callback, color_change_callback):
        """connect functions to draw the ball trail"""
        self._trail_callback = trail_callback
        self._color_change_callback = color_change_callback
    
    def set_audio_callbacks(self, **callbacks):
        """connect functions that play sounds"""
        self._audio_callbacks.update(callbacks)
    
    def set_visual_callbacks(self, **callbacks):
        """connect functions that trigger visual effects"""
        self._visual_callbacks.update(callbacks)
    
    def set_lighting_callbacks(self, **callbacks):
        """connect functions that control DMX lighting"""
        self._lighting_callbacks.update(callbacks)
    
    def set_difficulty(self, difficulty):
        """
        change the difficulty preset
        
        this will take effect the next time the game is reset
        """
        self.difficulty = difficulty
        self.apply_difficulty_preset(difficulty)
        
        # update AI difficulty immediately
        if self.ai:
            self.ai.difficulty = self.ai_difficulty
        
        logger.info(f"Difficulty changed to: {difficulty}")
