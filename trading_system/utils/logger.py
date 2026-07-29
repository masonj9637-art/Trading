import logging
import sys
import os

def setup_logger(name="trading_bot"):
    os.makedirs("logs", exist_ok=True)
    
    logger = logging.getLogger(name)
    logger.setLevel(logging.INFO)
    
    # Avoid adding handlers multiple times if instantiated multiple times
    if not logger.handlers:
        formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(message)s")
        
        file_handler = logging.FileHandler("logs/daily_execution.log")
        file_handler.setFormatter(formatter)
        
        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setFormatter(formatter)
        
        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)
        
    return logger

logger = setup_logger()
