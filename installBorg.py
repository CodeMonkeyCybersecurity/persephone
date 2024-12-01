#!/usr/bin/env python3

import subprocess
import sys

def error_exit(message):
    """Display an error message and exit."""
    print(message, file=sys.stderr)
    sys.exit(1)

def run_command(command, error_message):
    """Run a shell command and handle errors."""
    try:
        subprocess.run(command, shell=True, check=True, text=True)
    except subprocess.CalledProcessError:
        error_exit(error_message)

def main():
    print("Updating package list...")
    run_command("sudo apt update", "Failed to update package list.")

    print("Installing BorgBackup...")
    run_command("sudo apt install -y borgbackup", "Failed to install BorgBackup.")

    print("BorgBackup installation completed successfully.")

if __name__ == "__main__":
    main()
