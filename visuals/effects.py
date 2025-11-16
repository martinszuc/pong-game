"""Visual effects: particles, filters, flashes for special events"""

import cv2
import numpy as np
import random
import logging

logger = logging.getLogger(__name__)


class Particle:
    """Single particle for particle effects"""
    
    def __init__(self, x, y, velocity_x, velocity_y, color, lifetime=1.0):
        self.x = x
        self.y = y
        self.velocity_x = velocity_x
        self.velocity_y = velocity_y
        self.color = color
        self.lifetime = lifetime
        self.age = 0.0
    
    def update(self, delta_time):
        """Update particle position and age"""
        self.x += self.velocity_x * delta_time
        self.y += self.velocity_y * delta_time
        self.age += delta_time
    
    def is_alive(self):
        """Check if particle is still alive"""
        return self.age < self.lifetime


class ParticleSystem:
    """Manages particle effects"""
    
    def __init__(self):
        self.particles = []
    
    def add_explosion(self, x, y, count=20, color=(255, 255, 0)):
        """Add explosion particles at position"""
        for _ in range(count):
            angle = random.uniform(0, 2 * np.pi)
            speed = random.uniform(50, 200)
            velocity_x = np.cos(angle) * speed
            velocity_y = np.sin(angle) * speed
            lifetime = random.uniform(0.3, 0.8)
            particle = Particle(x, y, velocity_x, velocity_y, color, lifetime)
            self.particles.append(particle)
    
    def update(self, delta_time):
        """Update all particles"""
        self.particles = [p for p in self.particles if p.is_alive()]
        for particle in self.particles:
            particle.update(delta_time)
    
    def draw(self, frame):
        """Draw all particles on frame"""
        for particle in self.particles:
            if particle.is_alive():
                alpha = 1.0 - (particle.age / particle.lifetime)
                size = int(3 * alpha)
                if size > 0:
                    cv2.circle(frame, 
                             (int(particle.x), int(particle.y)), 
                             size, 
                             particle.color, 
                             -1)
    
    def clear(self):
        """Clear all particles"""
        self.particles = []


class VisualEffects:
    """Manages visual effects (flashes, filters, particles)"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        self.particle_system = ParticleSystem()
        self.flash_intensity = 0.0
        self.flash_color = (255, 255, 255)
        self.flash_decay_rate = 5.0
    
    def trigger_goal_flash(self, player_left=True):
        """Trigger flash effect when goal is scored"""
        self.flash_intensity = 1.0
        if player_left:
            self.flash_color = (0, 255, 0)
        else:
            self.flash_color = (255, 0, 0)
    
    def trigger_collision_particles(self, x, y):
        """Trigger particle explosion at collision point"""
        self.particle_system.add_explosion(x, y, count=15, color=(255, 255, 0))
    
    def update(self, delta_time):
        """Update all visual effects"""
        if self.flash_intensity > 0:
            self.flash_intensity = max(0.0, self.flash_intensity - self.flash_decay_rate * delta_time)
        self.particle_system.update(delta_time)
    
    def apply_effects(self, frame):
        """Apply all visual effects to frame"""
        if self.flash_intensity > 0:
            flash_overlay = np.zeros_like(frame)
            flash_overlay[:] = self.flash_color
            alpha = self.flash_intensity * 0.5
            frame = cv2.addWeighted(frame, 1.0 - alpha, flash_overlay, alpha, 0)
        
        self.particle_system.draw(frame)
        return frame
    
    def apply_color_filter(self, frame, filter_type='hot'):
        """Apply color map filter to frame"""
        if filter_type == 'hot':
            return cv2.applyColorMap(frame, cv2.COLORMAP_HOT)
        elif filter_type == 'cool':
            return cv2.applyColorMap(frame, cv2.COLORMAP_COOL)
        elif filter_type == 'plasma':
            return cv2.applyColorMap(frame, cv2.COLORMAP_PLASMA)
        else:
            return frame
