# app/logger.py

"""
Logging configuration module for the Plex Pre-Roll Automation application.

Sets up logging to both file and console with rotation to prevent log files from
growing indefinitely. Integrates logging with Flask's logger if a Flask app instance is provided.
"""

import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path
import os

def setup_logging(app=None):
    """
    Configures logging for the application with environment-based log levels.

    Args:
        app (Flask, optional): The Flask application instance to integrate logging with.
    """
    # Define the directory where log files will be stored
    log_dir = Path(__file__).parent.parent / 'logs'
    log_dir.mkdir(parents=True, exist_ok=True)  # Create the directory if it doesn't exist
    log_file = log_dir / 'app.log'  # Path to the log file

    # Retrieve log level from environment variable, default to INFO
    log_level = os.getenv('LOG_LEVEL', 'INFO').upper()
    numeric_level = getattr(logging, log_level, logging.INFO)

    # Get the root logger
    logger = logging.getLogger()
    
    # Prevent adding multiple handlers if logging is already configured
    if len(logger.handlers) > 0:
        return  # Logging is already set up; skip further configuration

    # Create a rotating file handler to manage log file size
    file_handler = RotatingFileHandler(
        log_file,
        maxBytes=5 * 1024 * 1024,  # 5MB per log file
        backupCount=5  # Keep up to 5 backup log files
    )
    file_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    file_handler.setFormatter(file_formatter)
    file_handler.setLevel(numeric_level)

    # Create a console handler to output logs to the terminal
    console_handler = logging.StreamHandler()
    console_formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    )
    console_handler.setFormatter(console_formatter)
    console_handler.setLevel(numeric_level)

    # Set the logging level for the root logger
    logger.setLevel(numeric_level)

    # Add both file and console handlers to the root logger
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    # If a Flask app instance is provided, integrate the handlers with Flask's logger
    if app:
        app.logger.handlers = logger.handlers
        app.logger.setLevel(logger.level)
        logging.info("Logging has been integrated with Flask's logger.")
