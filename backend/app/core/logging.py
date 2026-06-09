import logging
import sys
from typing import Any

def setup_logging(debug: bool = False) -> None:
    """
    Configure structured logging for the application.
    
    Args:
        debug: If True, set logging level to DEBUG, otherwise INFO.
    """
    log_level = logging.DEBUG if debug else logging.INFO
    
    # Define log format
    log_format = (
        "%(asctime)s | %(levelname)-8s | %(name)s:%(funcName)s:%(lineno)d - %(message)s"
    )
    
    # Configure root logger
    logging.basicConfig(
        level=log_level,
        format=log_format,
        handlers=[
            logging.StreamHandler(sys.stdout)
        ]
    )
    
    # Suppress verbose logging from external libraries if needed
    if not debug:
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("httpx").setLevel(logging.WARNING)

def get_logger(name: str) -> logging.Logger:
    """
    Get a named logger instance.
    
    Args:
        name: The name of the logger (usually __name__).
        
    Returns:
        A configured logging.Logger instance.
    """
    return logging.getLogger(name)
