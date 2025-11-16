DEFAULT_SPEED_INCREASE_FACTOR = 1.05
DEFAULT_MAX_SPEED_MULTIPLIER = 2.5


class Ball:
    def __init__(self, x, y, radius, velocity_x, velocity_y, 
                 speed_increase_factor=DEFAULT_SPEED_INCREASE_FACTOR, 
                 max_speed_multiplier=DEFAULT_MAX_SPEED_MULTIPLIER):
        self.position = [float(x), float(y)]
        self.radius = radius
        self.velocity = [float(velocity_x), float(velocity_y)]
        self.base_speed = (velocity_x**2 + velocity_y**2)**0.5
        self.speed = self.base_speed
        self.speed_increase_factor = speed_increase_factor
        self.max_speed = self.base_speed * max_speed_multiplier
    
    def update(self, delta_time):
        self.position[0] += self.velocity[0] * delta_time
        self.position[1] += self.velocity[1] * delta_time
    
    def reflect_x(self):
        self.velocity[0] = -self.velocity[0]
    
    def reflect_y(self):
        self.velocity[1] = -self.velocity[1]

    def increase_speed(self):
        self.speed = min(self.speed * self.speed_increase_factor, self.max_speed)

    def reset_speed(self):
        self.speed = self.base_speed

    def get_rect(self):
        return (
            self.position[0] - self.radius,
            self.position[1] - self.radius,
            self.position[0] + self.radius,
            self.position[1] + self.radius
        )


class Paddle:
    def __init__(self, x, y, width, height, speed):
        self.position = [float(x), float(y)]
        self.width = width
        self.height = height
        self.speed = speed
        self.direction = 0
    
    def update(self, delta_time, field_height):
        self.position[1] += self.direction * self.speed * delta_time
        min_y = 0
        max_y = field_height - self.height
        self.position[1] = max(min_y, min(max_y, self.position[1]))
    
    def move_up(self):
        self.direction = -1
    
    def move_down(self):
        self.direction = 1
    
    def stop(self):
        self.direction = 0
    
    def get_rect(self):
        return (
            self.position[0],
            self.position[1],
            self.position[0] + self.width,
            self.position[1] + self.height
        )
    
    def get_center_y(self):
        return self.position[1] + self.height / 2
