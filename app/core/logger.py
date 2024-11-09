import logging
import sys
from pathlib import Path
from logging.handlers import RotatingFileHandler
from datetime import datetime

class Logger:
    def __init__(self):
        # Create formatter
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Create handler (console only)
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        
        # Create logger
        self._logger = logging.getLogger("camera_dashboard")
        self._logger.setLevel(logging.INFO)
        
        # Add handler (console only)
        self._logger.addHandler(console_handler)
    
    @property
    def logger(self):
        return self._logger

# Create a singleton instance
logger = Logger().logger
