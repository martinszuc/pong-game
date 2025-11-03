"""
Logging configuration for the game
"""

import logging
import sys


def setup_logging(level=logging.DEBUG):
    """Setup logging configuration"""
    logging.basicConfig(
        level=level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler('pong_game.log', mode='w')
        ]
    )
    return logging.getLogger(__name__)


def get_logger(name):
    """Get a logger instance for a module"""
    return logging.getLogger(name)

