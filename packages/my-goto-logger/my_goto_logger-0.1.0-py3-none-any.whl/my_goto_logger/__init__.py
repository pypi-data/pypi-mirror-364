import logging
import os
from pathlib import Path
from logging.handlers import RotatingFileHandler

PROJECT_ROOT_PATH = os.path.dirname(os.path.realpath(__file__))  # pwd full path of project folder
PROJECT_LOG_FOLDER = Path(PROJECT_ROOT_PATH)
PROJECT_NAME = PROJECT_ROOT_PATH.split("\\")[-1]  # Project folder name
FILE_NAME = os.path.basename(__file__)


class CustomFormatter(logging.Formatter):
    grey = '\x1b[38;21m'
    blue = '\x1b[38;5;39m'
    yellow = '\x1b[38;5;226m'
    bold_red = '\x1b[38;5;196m'
    red = '\x1b[31;1m'
    reset = '\x1b[0m'
    fmt = "%(asctime)s : %(name)s : (%(filename)s:%(lineno)d) : %(levelname)s : %(message)s"

    def __init__(self, is_file=False):
        super().__init__()
        if is_file:
            self.FORMATS = {
            logging.DEBUG: self.fmt,
            logging.INFO: self.fmt,
            logging.WARNING: self.fmt,
            logging.ERROR: self.fmt,
            logging.CRITICAL: self.fmt
        }
        else:
            self.FORMATS = {
                logging.DEBUG: self.blue + self.fmt + self.reset,
                logging.INFO: self.grey + self.fmt + self.reset,
                logging.WARNING: self.yellow + self.fmt + self.reset,
                logging.ERROR: self.red + self.fmt + self.reset,
                logging.CRITICAL: self.bold_red + self.fmt + self.reset
            }

    def format(self, record):
        log_fmt = self.FORMATS.get(record.levelno)
        formatter = logging.Formatter(log_fmt)
        return formatter.format(record)

def start_logger():
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)
    stdout_handler = logging.StreamHandler()
    stdout_handler.setFormatter(CustomFormatter())
    log_file_file_path = os.path.join(PROJECT_LOG_FOLDER, f'{PROJECT_NAME}-{FILE_NAME}.log')
    logging.warning(f"Log File Path: {log_file_file_path}")
    log_file_handler = RotatingFileHandler(log_file_file_path, maxBytes=10*1024*1024, backupCount=5)
    log_file_handler.setFormatter(CustomFormatter(is_file=True))
    logger.addHandler(log_file_handler)
    logger.addHandler(stdout_handler)
