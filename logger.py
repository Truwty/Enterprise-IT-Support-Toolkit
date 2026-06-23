import logging
from logging.handlers import RotatingFileHandler
from config import LOG_DIR

LOG_FILE = LOG_DIR / "toolkit.log"

def setup_logger():
    logger = logging.getLogger("EnterpriseITToolkit")
    logger.setLevel(logging.DEBUG)

    # Console Handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # File Handler
    fh = RotatingFileHandler(LOG_FILE, maxBytes=5*1024*1024, backupCount=3)
    fh.setLevel(logging.DEBUG)

    formatter = logging.Formatter('%(asctime)s - %(levelname)s - [%(module)s] %(message)s')
    ch.setFormatter(formatter)
    fh.setFormatter(formatter)

    if not logger.handlers:
        logger.addHandler(ch)
        logger.addHandler(fh)

    return logger

log = setup_logger()
