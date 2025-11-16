import logging
import sys

LOG_FILE = 'pong_game.log'
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'


def setup_logging(level=logging.DEBUG):
    logging.basicConfig(
        level=level,
        format=LOG_FORMAT,
        handlers=[
            logging.StreamHandler(sys.stdout),
            logging.FileHandler(LOG_FILE, mode='w')
        ]
    )
    return logging.getLogger(__name__)


def get_logger(name):
    return logging.getLogger(name)

