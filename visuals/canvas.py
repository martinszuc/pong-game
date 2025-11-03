"""
Canvas system for ball trail painting
"""

import numpy as np
import cv2
import random
import logging

logger = logging.getLogger(__name__)


class Canvas:
    """Canvas that stores persistent trail lines painted by the ball"""
    
    def __init__(self, width, height):
        self.width = width
        self.height = height
        # Canvas stores the persistent trail
        self.canvas = np.zeros((height, width, 3), dtype=np.uint8)
        # Current trail color (BGR format for OpenCV)
        self.current_color = self._random_color()
        self.trail_thickness = 3
        
        logger.info(f"Canvas initialized: {width}x{height}")
    
    def _random_color(self):
        """Generate a random bright color"""
        return (
            random.randint(100, 255),  # B
            random.randint(100, 255),  # G
            random.randint(100, 255)   # R
        )
    
    def change_color(self):
        """Change to a new random color (called on bounce)"""
        self.current_color = self._random_color()
        logger.debug(f"Color changed to BGR: {self.current_color}")
    
    def paint_line(self, start_pos, end_pos):
        """Paint a line on the canvas from start to end position"""
        try:
            start_x, start_y = int(start_pos[0]), int(start_pos[1])
            end_x, end_y = int(end_pos[0]), int(end_pos[1])
            
            # Ensure coordinates are within bounds
            start_x = max(0, min(self.width - 1, start_x))
            start_y = max(0, min(self.height - 1, start_y))
            end_x = max(0, min(self.width - 1, end_x))
            end_y = max(0, min(self.height - 1, end_y))
            
            # Draw line on canvas (persistent)
            cv2.line(self.canvas, 
                    (start_x, start_y), 
                    (end_x, end_y), 
                    self.current_color, 
                    self.trail_thickness)
        except Exception as e:
            logger.error(f"Error painting line: {e}", exc_info=True)
    
    def clear(self):
        """Clear the canvas"""
        self.canvas = np.zeros((self.height, self.width, 3), dtype=np.uint8)
        logger.info("Canvas cleared")
    
    def get_canvas(self):
        """Get the current canvas state"""
        return self.canvas.copy()


