import logging
import os
from datetime import datetime

def get_logger(name: str):
    logger = logging.getLogger(name)
    
    if not logger.handlers:
        logger.setLevel(logging.INFO)
        
        # Format for logs
        formatter = logging.Formatter(
            '%(asctime)s - [%(levelname)s] - %(name)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        
        # 1. Console Handler (Prints to Colab Terminal)
        ch = logging.StreamHandler()
        ch.setFormatter(formatter)
        logger.addHandler(ch)
        
        # 2. File Handler (Saves to Google Drive Workspace)
        workspace = os.environ.get("APP_WORKSPACE_DIR", "./data")
        log_dir = f"{workspace}/logs"
        os.makedirs(log_dir, exist_ok=True)
        
        # Use today's date for log file
        date_str = datetime.now().strftime("%Y-%m-%d")
        log_file = f"{log_dir}/app_{date_str}.log"
        
        fh = logging.FileHandler(log_file, encoding='utf-8')
        fh.setFormatter(formatter)
        logger.addHandler(fh)
        
    return logger
