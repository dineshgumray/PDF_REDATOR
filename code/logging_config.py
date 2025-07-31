import logging
from logging.handlers import RotatingFileHandler
import config

def setup_logger(app_name):
    logger = logging.getLogger(app_name)
    logger.setLevel(getattr(logging, config.LOG_LEVEL))

    handler = RotatingFileHandler(config.LOG_FILE, maxBytes=5*1024*1024, backupCount=2)
    formatter = logging.Formatter('[%(asctime)s] %(levelname)s in %(module)s: %(message)s')
    handler.setFormatter(formatter)
    logger.addHandler(handler)

    return logger
