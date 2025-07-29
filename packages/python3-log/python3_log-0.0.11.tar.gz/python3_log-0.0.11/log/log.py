import os
import logging
import platform
from pathlib import Path
from datetime import datetime
from concurrent_log_handler import ConcurrentRotatingFileHandler


def get_logger():
    console_log_level=logging.getLevelName(os.environ.get('CONSOLE_LOG_LEVEL', 'INFO'))
    file_log_level=logging.getLevelName(os.environ.get('FILE_LOG_LEVEL', 'INFO'))
    log_dir=os.environ.get('LOG_DIR',"/var/log/my_app")
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)
    sys_name = platform.system()
    timestamp = datetime.now().strftime("%Y%m%d")
    if sys_name == "Windows":
        log_path = f"{os.environ.get('LOG_NAME','my_app')}.log"
    else:
        log_path= str(Path(log_dir) / f"{os.environ.get('LOG_NAME','my_app')}.log")
    file_handler = ConcurrentRotatingFileHandler(log_path, "a", 1024 * 1024 * 1024, 10)
    file_handler.setFormatter(logging.Formatter('%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(message)s'))
    log_format='%(asctime)s | %(levelname)s | %(filename)s:%(lineno)s | %(message)s'
    file_handler.setLevel(file_log_level)
    logger = logging.getLogger(os.environ.get('LOG_NAME','my_app'))
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level=console_log_level)
    console_handler.setFormatter(logging.Formatter(log_format))
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    logger.setLevel(logging.DEBUG)
    logger.propagate = False
    return logger
