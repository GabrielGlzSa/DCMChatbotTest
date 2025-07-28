import logging
import sys
import os
from datetime import datetime

# Create a logger instance
logger = logging.getLogger("dcm_chatbot")

# Prevent duplicate handlers if logger is imported multiple times
if not logger.handlers:

    # Set log level (adjust as needed: DEBUG, INFO, WARNING, ERROR, CRITICAL)
    logger.setLevel(logging.DEBUG)

    # Create a custom formatter
    formatter = logging.Formatter(
        fmt='%(asctime)s - %(levelname)s -%(name)s- %(funcName)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Ensure directory exists
    log_path = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data', 'logs'))
    os.makedirs(log_path, exist_ok=True)

    
    log_filename = f"{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}_app.log"
    file_path = os.path.join(log_path, log_filename)

    # Create a file handler
    file_handler = logging.FileHandler(file_path, mode='w', encoding='utf-8')
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)

    # Console handler with output to stdout
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # Show only warnings for logs of following libraries.
    for logger_name in ['requests', 'langchain_huggingface']:
        logging.getLogger(logger_name).setLevel(logging.WARNING)