"""
Logging configuration for the Trade Simulator
"""
import logging
import sys
from logging.handlers import RotatingFileHandler
from src.config import LOG_LEVEL, LOG_FORMAT, LOG_FILE

def setup_logging():
    """Set up logging configuration"""
    # Get root logger
    root_logger = logging.getLogger()
    
    # Clear existing handlers
    for handler in root_logger.handlers[:]:
        root_logger.removeHandler(handler)
    
    # Set log level
    level = getattr(logging, LOG_LEVEL.upper(), logging.INFO)
    root_logger.setLevel(level)
    
    # Create formatters
    formatter = logging.Formatter(LOG_FORMAT)
    
    # Create console handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    root_logger.addHandler(console_handler)
    
    # Create file handler
    file_handler = RotatingFileHandler(
        LOG_FILE, 
        maxBytes=10*1024*1024,  # 10 MB
        backupCount=5
    )
    file_handler.setFormatter(formatter)
    root_logger.addHandler(file_handler)
    
    # Log startup message
    root_logger.info("Logging initialized")