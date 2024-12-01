import logging
import traceback
from datetime import datetime

class ErrorLogger:
    def __init__(self, log_file="error_log.log"):
        """
        Initialize the error logger with a specified log file.
        :param log_file: Path to the log file
        """
        self.log_file = log_file
        logging.basicConfig(
            filename=self.log_file,
            level=logging.ERROR,
            format="%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )

    def log_error(self, error_message):
        """
        Log an error message with a detailed traceback.
        :param error_message: Custom error message to include in the log
        """
        formatted_traceback = traceback.format_exc()
        logging.error(f"{error_message}\n{formatted_traceback}")

    def log_custom(self, message, level=logging.INFO):
        """
        Log a custom message at the specified logging level.
        :param message: Custom message to log
        :param level: Logging level (default is INFO)
        """
        logging.log(level, message)

# Example usage:
# logger = ErrorLogger("my_script_errors.log")
# try:
#     1 / 0  # Simulate an error
# except Exception as e:
#     logger.log_error("An error occurred during division")
