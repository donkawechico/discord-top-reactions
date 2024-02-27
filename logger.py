import pdb
import logging
from logging.handlers import RotatingFileHandler
import os
import pprint

# Define constants
LOG_FILENAME = 'log.txt'
MAX_LOG_SIZE_BYTES = 5 * 1024 * 1024  # Set a maximum log size of 5MB
BACKUP_COUNT = 1  # We'll keep one backup log file (log.txt.1)

# Set up logging
logging.basicConfig(
    level=logging.DEBUG,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[RotatingFileHandler(LOG_FILENAME, maxBytes=MAX_LOG_SIZE_BYTES, backupCount=BACKUP_COUNT)]
)

logger = logging.getLogger()

PRINT_TO_CONSOLE = True

def _print(message):
  if PRINT_TO_CONSOLE:
    print(message)

def prettify(message, pretty=False):
    if pretty:
        return pprint.pformat(message, indent=4)
    else:
        return message


def log_info(message, pretty=False):
    message = prettify(message, pretty)
    logger.info(message)
    _print(message)
    _check_and_trim_log()

def log_error(message, pretty=False):
    message = prettify(message, pretty)
    logger.error(message)
    _print(message)
    _check_and_trim_log()

def log_warning(message, pretty=False):
    message = prettify(message, pretty)
    logger.warning(message)
    _print(message)
    _check_and_trim_log()

def log_debug(message, pretty=False):
    # pdb.set_trace()
    message = prettify(message, pretty)
    logger.debug(message)
    _print(message)
    _check_and_trim_log()

def _check_and_trim_log():
    if os.path.exists(LOG_FILENAME) and os.path.getsize(LOG_FILENAME) > MAX_LOG_SIZE_BYTES:
        with open(LOG_FILENAME, 'r+') as log_file:
            log_file.seek(-MAX_LOG_SIZE_BYTES, os.SEEK_END)
            log_file.readline()  # Skip potentially partial line
            remaining_lines = log_file.readlines()
            log_file.seek(0)
            log_file.truncate()
            log_file.writelines(remaining_lines)

if __name__ == "__main__":
    # Test the logger
    log_info("This is an info message.")
    log_error("This is an error message.")
