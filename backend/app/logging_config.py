import logging
import os
from logging.handlers import RotatingFileHandler

logger = logging.getLogger("vectorrt")

LOG_DIR = os.getenv("VECTORRT_DATA_DIR", "./data")
LOG_FILE = os.path.join(LOG_DIR, "vectorrt.log")
MAX_LOG_BYTES = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3


def configure_logging() -> None:
    level = os.getenv("LOG_LEVEL", "INFO").upper()
    formatter = logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s")

    os.makedirs(LOG_DIR, exist_ok=True)
    file_handler = RotatingFileHandler(LOG_FILE, maxBytes=MAX_LOG_BYTES, backupCount=LOG_BACKUP_COUNT)
    file_handler.setFormatter(formatter)

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    logging.basicConfig(level=level, handlers=[stream_handler, file_handler])
