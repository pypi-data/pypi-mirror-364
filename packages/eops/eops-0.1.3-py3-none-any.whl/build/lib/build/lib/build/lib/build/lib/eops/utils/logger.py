# eops/utils/logger.py
import logging
import sys
from typing import Optional
from pathlib import Path # <-- Import Path

_loggers = {}

class InstanceFilter(logging.Filter):
    def __init__(self, instance_id: str):
        super().__init__()
        self.instance_id = instance_id
    def filter(self, record):
        record.instance_id = self.instance_id
        return True

def setup_logger(instance_id: Optional[str] = "main", log_file: Optional[Path] = None): # <-- Add log_file param
    """Sets up a logger that is unique to a given instance_id."""
    if instance_id in _loggers:
        return _loggers[instance_id]

    logger = logging.getLogger(f"eops.{instance_id}")
    logger.propagate = False
    if logger.hasHandlers():
        logger.handlers.clear() # Clear existing handlers to reconfigure
        
    logger.setLevel(logging.INFO)
    formatter = logging.Formatter(
        '%(asctime)s - eops [inst:%(instance_id)s] - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )
    
    # Console Handler
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)

    # --- FIX: Add File Handler if log_file is provided ---
    if log_file:
        log_file.parent.mkdir(parents=True, exist_ok=True)
        file_handler = logging.FileHandler(log_file, mode='a', encoding='utf-8')
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    
    logger.addFilter(InstanceFilter(instance_id))
    _loggers[instance_id] = logger
    return logger

log = setup_logger("framework")