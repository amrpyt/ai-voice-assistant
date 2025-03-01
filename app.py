"""
Main Application Module

This module serves as the entry point for the AI voice assistant application.
"""
import os
import sys
import logging
import logging.config
from pathlib import Path

import config
from voice_assistant.assistant_manager import AssistantManager
from ui.main_window import MainWindow

def setup_logging():
    """Set up logging configuration."""
    logging_config = {
        'version': 1,
        'disable_existing_loggers': False,
        'formatters': {
            'standard': {
                'format': '%(asctime)s [%(levelname)s] %(name)s: %(message)s'
            },
        },
        'handlers': {
            'console': {
                'class': 'logging.StreamHandler',
                'level': config.LOG_LEVEL,
                'formatter': 'standard',
                'stream': 'ext://sys.stdout',
            },
            'file': {
                'class': 'logging.FileHandler',
                'level': config.LOG_LEVEL,
                'formatter': 'standard',
                'filename': config.LOG_FILE,
                'mode': 'a',
            },
        },
        'root': {
            'level': config.LOG_LEVEL,
            'handlers': ['console', 'file'],
        },
    }
    
    # Create log directory if it doesn't exist
    log_dir = os.path.dirname(config.LOG_FILE)
    if log_dir and not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    logging.config.dictConfig(logging_config)

def main():
    """Main application entry point."""
    # Set up logging
    setup_logging()
    logger = logging.getLogger(__name__)
    
    logger.info("Starting AI Voice Assistant")
    logger.info(f"Using RAG API endpoint: {config.RAG_API_ENDPOINT}")
    logger.info(f"Default user: {config.DEFAULT_USER_NAME} ({config.DEFAULT_USER_TYPE})")
    
    try:
        # Create the assistant manager
        assistant_manager = AssistantManager()
        
        # Create and run the UI
        app = MainWindow(assistant_manager)
        app.run()
        
        logger.info("Application closed")
        return 0
    except Exception as e:
        logger.exception(f"Error in main application: {e}")
        return 1

if __name__ == "__main__":
    sys.exit(main())