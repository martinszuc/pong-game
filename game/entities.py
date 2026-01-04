"""
entities.py - Game objects (ball and paddles)

This file defines the basic game objects that exist in the pong game.
Each object knows how to move and update itself.
"""

# how much faster the ball gets after each paddle hit (5% faster)
DEFAULT_SPEED_INCREASE_FACTOR = 1.05

# maximum speed the ball can reach (2.5x the starting speed)
DEFAULT_MAX_SPEED_MULTIPLIER = 2.5


class Ball:
    """
    the pong ball
    
    this class represents the ball that bounces around the screen.
    it knows its position, size, and how fast it's moving
    """
    
    def __init__(self, x, y, radius, velocity_x, velocity_y, 
                 speed_increase_factor=DEFAULT_SPEED_INCREASE_FACTOR, 
                 max_speed_multiplier=DEFAULT_MAX_SPEED_MULTIPLIER):
        """create a new ball at position (x, y) with given size and velocity"""
        self.position = [float(x), float(y)]  # where the ball is [x, y]
        self.radius = radius  # how big the ball is
        self.velocity = [float(velocity_x), float(velocity_y)]  # how fast it's moving [x_speed, y_speed]
        
        # calculate the starting speed using pythagorean theorem
        self.base_speed = (velocity_x**2 + velocity_y**2)**0.5
        self.speed = self.base_speed
        
        # how much to speed up after each hit
        self.speed_increase_factor = speed_increase_factor
        
        # maximum allowed speed (so it doesn't get too crazy fast)
        self.max_speed = self.base_speed * max_speed_multiplier
    
    def update(self, delta_time):
        """
        move the ball based on its velocity
        delta_time is how much time has passed (in seconds)
        """
        self.position[0] += self.velocity[0] * delta_time  # move horizontally
        self.position[1] += self.velocity[1] * delta_time  # move vertically
    
    def reflect_x(self):
        """bounce the ball horizontally (when it hits a paddle)"""
        self.velocity[0] = -self.velocity[0]
    
    def reflect_y(self):
        """bounce the ball vertically (when it hits top or bottom wall)"""
        self.velocity[1] = -self.velocity[1]

    def increase_speed(self):
        """make the ball go faster (happens after each paddle hit)"""
        self.speed = min(self.speed * self.speed_increase_factor, self.max_speed)

    def reset_speed(self):
        """set the ball back to its starting speed"""
        self.speed = self.base_speed

    def get_rect(self):
        """
        get the ball's bounding box for collision detection
        returns (left, top, right, bottom) coordinates
        """
        return (
            self.position[0] - self.radius,  # left edge
            self.position[1] - self.radius,  # top edge
            self.position[0] + self.radius,  # right edge
            self.position[1] + self.radius   # bottom edge
        )


class Paddle:
    """
    a pong paddle
    
    this class represents one of the paddles that hits the ball.
    it can move up and down within the game field
    """
    
    def __init__(self, x, y, width, height, speed):
        """create a new paddle at position (x, y) with given size and speed"""
        self.position = [float(x), float(y)]  # where the paddle is [x, y]
        self.width = width  # how wide the paddle is
        self.height = height  # how tall the paddle is
        self.speed = speed  # how fast it moves (pixels per second)
        self.direction = 0  # which way it's moving: -1=up, 0=stopped, 1=down
    
    def update(self, delta_time, field_height):
        """
        move the paddle based on its direction
        also make sure it doesn't go off the top or bottom of the screen
        """
        # move the paddle (speed * direction * time)
        self.position[1] += self.direction * self.speed * delta_time
        
        # keep paddle within the game field boundaries
        min_y = 0  # top of screen
        max_y = field_height - self.height  # bottom of screen (minus paddle height)
        self.position[1] = max(min_y, min(max_y, self.position[1]))
    
    def move_up(self):
        """start moving the paddle upward"""
        self.direction = -1
    
    def move_down(self):
        """start moving the paddle downward"""
        self.direction = 1
    
    def stop(self):
        """stop moving the paddle"""
        self.direction = 0
    
    def get_rect(self):
        """
        get the paddle's bounding box for collision detection
        returns (left, top, right, bottom) coordinates
        """
        return (
            self.position[0],  # left edge
            self.position[1],  # top edge
            self.position[0] + self.width,  # right edge
            self.position[1] + self.height  # bottom edge
        )
    
    def get_center_y(self):
        """get the y-coordinate of the paddle's center (used for angled bounces)"""
        return self.position[1] + self.height / 2
