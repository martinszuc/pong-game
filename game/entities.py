"""
Game entities: Ball and Paddle classes
"""


class Ball:
    """Represents the pong ball with position, velocity, and collision detection"""

    def __init__(self, x, y, radius, velocity_x, velocity_y, speed_increase_factor=1.05, max_speed_multiplier=2.5):
        self.position = [float(x), float(y)]
        self.radius = radius
        self.velocity = [float(velocity_x), float(velocity_y)]
        self.base_speed = (velocity_x**2 + velocity_y**2)**0.5  # Store initial speed
        self.speed = self.base_speed
        self.speed_increase_factor = speed_increase_factor  # Speed multiplier per paddle hit (default 5% increase)
        self.max_speed = self.base_speed * max_speed_multiplier  # Maximum speed cap
    
    def update(self, delta_time):
        """Update position based on velocity"""
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time
    
    def reflect_x(self):
        """Reverse horizontal velocity (ball hit left/right wall)"""
        self.velocity[0] = -self.velocity[0]
    
    def reflect_y(self):
        """Reverse vertical velocity (ball hit top/bottom wall)"""
        self.velocity[1] = -self.velocity[1]

    def increase_speed(self):
        """Increase ball speed by the speed increase factor, up to max speed"""
        self.speed = min(self.speed * self.speed_increase_factor, self.max_speed)

    def reset_speed(self):
        """Reset ball speed to base speed"""
        self.speed = self.base_speed

    def get_rect(self):
        """Return bounding box for collision detection"""
        return (
            self.position[0] - self.radius,
            self.position[1] - self.radius,
            self.position[0] + self.radius,
            self.position[1] + self.radius
        )


class Paddle:
    """Represents a paddle with position, size, and movement"""
    
    def __init__(self, x, y, width, height, speed):
        self.position = [float(x), float(y)]
        self.width = width
        self.height = height
        self.speed = speed
        self.direction = 0  # -1: up, 0: stop, 1: down
    
    def update(self, delta_time, field_height):
        """Update paddle position based on direction, constrained to field"""
        old_y = self.position[1]
        self.position[1] += self.direction * self.speed * delta_time
        
        # constrain to field boundaries
        min_y = 0
        max_y = field_height - self.height
        self.position[1] = max(min_y, min(max_y, self.position[1]))
        
        # If paddle hit boundary and can't move further, don't change direction
        # (direction stays the same so it can move away from boundary when key changes)
    
    def move_up(self):
        """Set direction to move up"""
        self.direction = -1
    
    def move_down(self):
        """Set direction to move down"""
        self.direction = 1
    
    def stop(self):
        """Stop paddle movement"""
        self.direction = 0
    
    def get_rect(self):
        """Return bounding box for collision detection"""
        return (
            self.position[0],
            self.position[1],
            self.position[0] + self.width,
            self.position[1] + self.height
        )
    
    def get_center_y(self):
        """Return y-coordinate of paddle center"""
        return self.position[1] + self.height / 2

