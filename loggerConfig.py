import logging

def setup_logger(name='my_logger', log_file='app.log', level=logging.INFO):
    logger = logging.getLogger(name)
    
    if not logger.handlers:  # Only add handlers once
        # File handler
        file_handler = logging.FileHandler(log_file)
        file_handler.setLevel(level)
        
        # Console handler
        console_handler = logging.StreamHandler()
        console_handler.setLevel(level)
        
        # Formatter
        formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')
        file_handler.setFormatter(formatter)
        console_handler.setFormatter(formatter)
        
        # Add handlers
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
    
    logger.setLevel(level)
    return logger

logger = setup_logger()