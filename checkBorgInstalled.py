import os
import shutil
import sys

def checkBorgInstalled():
    """Checks if BorgBackup is installed."""
    message = "Checking if BorgBackup is installed..."
    logging.info(message)
    print(message)

    if shutil.which('borg') is None:  # Check if Borg is in the system PATH
        error_exit("BorgBackup is not installed. Please install it first.")
    else:
        success_message = "BorgBackup is installed."
        logging.info(success_message)
        print(success_message)

# Example usage
if __name__ == "__main__":
    checkBorgInstalled()
