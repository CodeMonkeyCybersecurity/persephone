#!/usr/bin/env python3

import os
import subprocess
import sys

LOGFILE = "restore.log"

def log_message(message):
    """Log a message to the console and a log file."""
    print(message)
    with open(LOGFILE, "a") as log_file:
        log_file.write(message + "\n")

def error_exit(message):
    """Display an error message, log it, and exit."""
    log_message(message)
    sys.exit(1)

def check_borg_installed():
    """Check if Borg is installed."""
    try:
        subprocess.run(["borg", "--version"], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except FileNotFoundError:
        error_exit("BorgBackup is not installed. Please install it before running this script.")

def test_restore():
    """Test the restore operation using Borg."""
    check_borg_installed()

    # Check if BORG_REPO is set
    borg_repo = os.getenv("BORG_REPO")
    if not borg_repo:
        error_exit("BORG_REPO is not set. Exiting.")

    # Prompt user for inputs
    archive_name = input("Enter the archive name to restore: ")
    dest_dir = input("Enter the destination directory: ")

    log_message(f"Restoring archive {archive_name} to {dest_dir}")

    # Run the Borg extract command
    try:
        subprocess.run(["borg", "extract", f"{borg_repo}::{archive_name}", dest_dir], check=True)
        log_message("Restore operation completed.")
    except subprocess.CalledProcessError as e:
        error_exit(f"Restore operation failed: {e}")

if __name__ == "__main__":
    test_restore()
