import logging
import os
from logging.handlers import RotatingFileHandler
from app.core.config import settings


def setup_logger():
    """Setup application logger"""
    # Create logs directory if it doesn't exist
    log_dir = "logs"
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    
    # Configure logging
    logging.basicConfig(
        level=getattr(logging, settings.LOG_LEVEL.upper()),
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[
            # File handler with rotation
            RotatingFileHandler(
                os.path.join(log_dir, "app.log"),
                maxBytes=10485760,  # 10MB
                backupCount=5
            ),
            # Console handler
            logging.StreamHandler()
        ]
    )
    
    return logging.getLogger(__name__)


logger = setup_logger()
