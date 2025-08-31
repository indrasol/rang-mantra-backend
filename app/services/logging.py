import logging
from logging.handlers import RotatingFileHandler
import os
import sys

def setup_logging():
    """Set up logging configuration for the application."""
    logger = logging.getLogger("rangmantra")
    logger.setLevel(logging.INFO)
    
    # Create a formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # Try to create a file handler if possible
    try:
        log_dir = "logs"
        os.makedirs(log_dir, exist_ok=True)
        file_handler = RotatingFileHandler(
            os.path.join(log_dir, "rangmantra.log"), 
            maxBytes=10485760,  # 10MB
            backupCount=3
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except (IOError, PermissionError):
        logger.warning("Unable to create log file. Logging to console only.")
    
    return logger
