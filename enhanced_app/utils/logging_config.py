import logging
import sys
from logging.handlers import RotatingFileHandler

def configure_logging():
    root_logger = logging.getLogger()
    root_logger.setLevel(logging.INFO)

    # Console handler (existing)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    console_handler.setFormatter(console_formatter)

    # File handler (new)
    file_handler = RotatingFileHandler('roadmap_generation.log', maxBytes=10*1024*1024, backupCount=5)
    file_handler.setLevel(logging.INFO)
    file_formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    file_handler.setFormatter(file_formatter)

    root_logger.addHandler(console_handler)
    root_logger.addHandler(file_handler)

    return root_logger

logger = configure_logging()
