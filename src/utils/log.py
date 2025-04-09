import logging
from datetime import datetime

# Uncomment only if you want to suppress logs from the libraries
# and the function logging.basicConfig is used
# Suppress logs from python-telegram-bot
#logging.getLogger("telegram").setLevel(logging.WARNING)

# Suppress logs from httpx and httpcore
#logging.getLogger("httpx").setLevel(logging.WARNING)
#logging.getLogger("httpcore").setLevel(logging.WARNING)

class Log:
    EXCEPTION_LOG_FILE = "exceptions.log"
    FORMAT = "[%(asctime)s] [%(levelname)s] [%(name)s] %(message)s"
    DATE_FORMAT = "%Y-%m-%d %H:%M:%S"

    # Define colors
    COLORS = {
        "ERROR": "\033[91m",  # Red
        "WARN": "\033[93m",   # Yellow
        "INFO": "\033[94m",   # Blue
        "RESET": "\033[0m"    # Reset
    }

    def __init__(self, class_name):
        self.class_name = class_name
        self.logger = logging.getLogger(class_name)
        
        # Configure basic logging settings
        # Note: If you enable this, you may need to handle the log level of python-telegram-bot components
        # to avoid excessive logging from its internal modules.
        # logging.basicConfig(
        #     filename=self.EXCEPTION_LOG_FILE,
        #     level=logging.DEBUG,
        #     format=self.FORMAT,
        #     datefmt=self.DATE_FORMAT
        # )
        
        self.logger.setLevel(logging.DEBUG)  # Set the logging level for this logger

        # Create a file handler if it doesn't already exist
        if not self.logger.handlers:
            file_handler = logging.FileHandler(self.EXCEPTION_LOG_FILE)
            file_handler.setLevel(logging.DEBUG)
            formatter = logging.Formatter(self.FORMAT, datefmt=self.DATE_FORMAT)
            file_handler.setFormatter(formatter)
            self.logger.addHandler(file_handler)

    def _log_with_color(self, level, message):
        color = self.COLORS.get(level, self.COLORS["RESET"])
        reset = self.COLORS["RESET"]
        print(f"{color}[{datetime.now().strftime(self.DATE_FORMAT)}] [{level}] [{self.class_name}] {message}{reset}")

    def error(self, message):
        self.logger.error(message)
        self._log_with_color("ERROR", message)

    def warn(self, message):
        self.logger.warning(message)
        self._log_with_color("WARN", message)

    def info(self, message):
        self.logger.info(message)
        self._log_with_color("INFO", message)