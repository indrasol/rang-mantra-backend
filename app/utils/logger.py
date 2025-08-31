import logging
import traceback
import sys

logger = logging.getLogger("rangmantra")

def log_info(message):
    """Log an info message"""
    logger.info(message)

def log_warning(message):
    """Log a warning message"""
    logger.warning(message)

def log_error(message, exc_info=False):
    """Log an error message"""
    logger.error(message, exc_info=exc_info)

def log_exception(message):
    """Log an exception with traceback"""
    exc_type, exc_value, exc_traceback = sys.exc_info()
    logger.error(f"{message}: {exc_value}")
    logger.error("Traceback:", exc_info=(exc_type, exc_value, exc_traceback))

def log_debugger(message):
    """Log a debug message"""
    logger.debug(message)
