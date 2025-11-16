import cv2
import numpy as np
import random
import logging

logger = logging.getLogger(__name__)

DEFAULT_PARTICLE_LIFETIME = 1.0
DEFAULT_EXPLOSION_COUNT = 20
COLLISION_PARTICLE_COUNT = 15
MIN_PARTICLE_SPEED = 50
MAX_PARTICLE_SPEED = 200
MIN_PARTICLE_LIFETIME = 0.3
MAX_PARTICLE_LIFETIME = 0.8
PARTICLE_BASE_SIZE = 3
FLASH_DECAY_RATE = 5.0
FLASH_MAX_INTENSITY = 1.0
FLASH_ALPHA_MULTIPLIER = 0.5


class Particle:
    def __init__(self, x, y, velocity_x, velocity_y, color, lifetime=DEFAULT_PARTICLE_LIFETIME):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
    
    def update(self, delta_time):
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.age += delta_time
    
    def is_alive(self):
        return self.age < self.lifetime


class ParticleSystem:
    def __init__(self):
        self.particles = []
    
    def add_explosion(self, x, y, count=DEFAULT_EXPLOSION_COUNT, color=(255, 255, 0)):
        for _ in range(count):
            angle = random.uniform(0, 2 * np.pi)
            speed = random.uniform(MIN_PARTICLE_SPEED, MAX_PARTICLE_SPEED)
            velocity_x = np.cos(angle) * speed
            velocity_y = np.sin(angle) * speed
            lifetime = random.uniform(MIN_PARTICLE_LIFETIME, MAX_PARTICLE_LIFETIME)
            particle = Particle(x, y, velocity_x, velocity_y, color, lifetime)
            self.particles.append(particle)
    
    def update(self, delta_time):
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update(delta_time)
    
    def draw(self, frame):
        for particle in self.particles:
            if particle.is_alive():
                alpha = 1.0 - (particle.age / particle.lifetime)
                size = int(PARTICLE_BASE_SIZE * alpha)
                if size > 0:
                    cv2.circle(frame, 
                             (int(particle.x), int(particle.y)), 
                             size, 
                             particle.color, 
                             -1)
    
    def clear(self):
        self.particles = []


class VisualEffects:
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particle_system = ParticleSystem()
        self.flash_intensity = 0.0
        self.flash_color = (255, 255, 255)
        self.flash_decay_rate = FLASH_DECAY_RATE
    
    def trigger_goal_flash(self, player_left=True):
        self.flash_intensity = FLASH_MAX_INTENSITY
        if player_left:
            self.flash_color = (0, 255, 0)
        else:
            self.flash_color = (255, 0, 0)
    
    def trigger_collision_particles(self, x, y):
        self.particle_system.add_explosion(x, y, count=COLLISION_PARTICLE_COUNT, color=(255, 255, 0))
    
    def update(self, delta_time):
        if self.flash_intensity > 0:
            self.flash_intensity = max(0.0, self.flash_intensity - self.flash_decay_rate * delta_time)
        self.particle_system.update(delta_time)
    
    def apply_effects(self, frame):
        if self.flash_intensity > 0:
            flash_overlay = np.zeros_like(frame)
            flash_overlay[:] = self.flash_color
            alpha = self.flash_intensity * FLASH_ALPHA_MULTIPLIER
            frame = cv2.addWeighted(frame, 1.0 - alpha, flash_overlay, alpha, 0)
        
        self.particle_system.draw(frame)
        return frame
    
    def apply_color_filter(self, frame, filter_type='hot'):
        if filter_type == 'hot':
            return cv2.applyColorMap(frame, cv2.COLORMAP_HOT)
        elif filter_type == 'cool':
            return cv2.applyColorMap(frame, cv2.COLORMAP_COOL)
        elif filter_type == 'plasma':
            return cv2.applyColorMap(frame, cv2.COLORMAP_PLASMA)
        else:
            return frame
