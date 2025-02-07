#!/usr/bin/env python3
"""
createPersephoneBackup.py

This script performs a Restic backup by prompting for required configuration
values, storing those values in a config file (.persephone_backup.conf) for future
runs, and then executing the Restic commands.
"""

import os
import subprocess

CONFIG_FILE = ".persephone_backup.conf"


def load_config(config_file):
    """
    Loads configuration from the config file if it exists.
    Expected file format:
        REPO_FILE="/root/.restic-repo"
        PASS_FILE="/root/.restic-password"
        BACKUP_PATHS_STR="/root /home /var /etc /srv /usr /opt"
    Returns a dictionary with the configuration values.
    """
    config = {}
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    # Remove surrounding quotes if present.
                    value = value.strip().strip('"').strip("'")
                    config[key] = value
    return config


def prompt_input(prompt_message, default_val=None):
    """
    Prompts the user for input with an optional default.
    If the user just presses Enter and a default exists, the default is returned.
    """
    if default_val:
        prompt = f"{prompt_message} [{default_val}]: "
    else:
        prompt = f"{prompt_message}: "
    while True:
        response = input(prompt).strip()
        if response == "" and default_val is not None:
            return default_val
        elif response != "":
            return response
        else:
            print("Error: Input cannot be empty. Please enter a valid value.")


def save_config(config_file, repo_file, pass_file, backup_paths_str):
    """
    Saves the configuration values to the config file.
    """
    with open(config_file, "w") as f:
        f.write(f'REPO_FILE="{repo_file}"\n')
        f.write(f'PASS_FILE="{pass_file}"\n')
        f.write(f'BACKUP_PATHS_STR="{backup_paths_str}"\n')


def main():
    # Load configuration if available.
    config = load_config(CONFIG_FILE)
    default_repo = config.get("REPO_FILE", "/root/.restic-repo")
    default_pass = config.get("PASS_FILE", "/root/.restic-password")
    default_backup_paths = config.get("BACKUP_PATHS_STR", "/root /home /var /etc /srv /usr /opt")

    print("=== Restic Backup Configuration ===")
    repo_file = prompt_input("Enter the restic repository file path", default_repo)
    pass_file = prompt_input("Enter the restic password file path", default_pass)
    backup_paths_str = prompt_input("Enter backup paths (space-separated)", default_backup_paths)

    # Save the entered configuration for future runs.
    save_config(CONFIG_FILE, repo_file, pass_file, backup_paths_str)

    # Convert the backup paths (a space-separated string) into a list.
    backup_paths = backup_paths_str.split()

    # Run the backup command.
    print("\nRunning Restic backup...")
    backup_cmd = [
        "sudo",
        "restic",
        "--repository-file", repo_file,
        "--password-file", pass_file,
        "--verbose",
        "backup",
    ] + backup_paths

    subprocess.run(backup_cmd, check=True)

    # Check snapshots.
    print("Backup completed. Checking snapshots...")
    snapshots_cmd = [
        "sudo",
        "restic",
        "--repository-file", repo_file,
        "--password-file", pass_file,
        "snapshots",
    ]
    subprocess.run(snapshots_cmd, check=True)

    print("Restic backup and snapshot check complete.")


if __name__ == "__main__":
    main()
