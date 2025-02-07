#!/usr/bin/env python3
"""
createPersephoneBackup.py

This script performs a Restic backup by prompting for required configuration
values—including AWS credentials—storing those values in a config file 
(.persephone_backup.conf) for future runs, and then executing the Restic commands.
"""

import os
import subprocess
import getpass

CONFIG_FILE = ".persephone_backup.conf"


def load_config(config_file):
    """
    Loads configuration from the config file if it exists.
    Expected file format (one key="value" per line):
      REPO_FILE="s3:https://s3api.cybermonkey.dev/restic"
      PASS_FILE="/root/.restic-password"
      BACKUP_PATHS_STR="/root /home /var /etc /srv /usr /opt"
      AWS_ACCESS_KEY_ID="..."
      AWS_SECRET_ACCESS_KEY="..."
      AWS_DEFAULT_REGION="us-east-1"
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


def prompt_input(prompt_message, default_val=None, hidden=False):
    """
    Prompts the user for input with an optional default.
    If hidden=True, the input will be hidden (useful for sensitive data).
    """
    if default_val:
        prompt = f"{prompt_message} [{default_val}]: "
    else:
        prompt = f"{prompt_message}: "
    while True:
        if hidden:
            response = getpass.getpass(prompt).strip()
        else:
            response = input(prompt).strip()
        if response == "" and default_val is not None:
            return default_val
        elif response != "":
            return response
        else:
            print("Error: Input cannot be empty. Please enter a valid value.")


def save_config(config_file, config):
    """
    Saves the configuration dictionary to the config file.
    """
    with open(config_file, "w") as f:
        for key, value in config.items():
            f.write(f'{key}="{value}"\n')


def main():
    # Load configuration if available.
    config = load_config(CONFIG_FILE)

    # Get default values from the config or use sensible defaults.
    default_repo = config.get("REPO_FILE", "s3:https://s3api.cybermonkey.dev/restic")
    default_pass_file = config.get("PASS_FILE", "/root/.restic-password")
    default_backup_paths = config.get("BACKUP_PATHS_STR", "/root /home /var /etc /srv /usr /opt")

    # AWS credentials defaults.
    default_aws_access_key = config.get("AWS_ACCESS_KEY_ID", "")
    default_aws_secret_key = config.get("AWS_SECRET_ACCESS_KEY", "")
    default_aws_region = config.get("AWS_DEFAULT_REGION", "us-east-1")

    print("=== Restic Backup Configuration ===")
    repo_file = prompt_input("Enter the restic repository file path", default_repo)
    pass_file = prompt_input("Enter the restic password file path", default_pass_file)
    backup_paths_str = prompt_input("Enter backup paths (space-separated)", default_backup_paths)

    print("\n=== AWS Credentials ===")
    aws_access_key = prompt_input("Enter AWS_ACCESS_KEY_ID", default_aws_access_key)
    aws_secret_key = prompt_input("Enter AWS_SECRET_ACCESS_KEY", default_aws_secret_key, hidden=True)
    aws_region = prompt_input("Enter AWS_DEFAULT_REGION", default_aws_region)

    # Update configuration dictionary.
    config["REPO_FILE"] = repo_file
    config["PASS_FILE"] = pass_file
    config["BACKUP_PATHS_STR"] = backup_paths_str
    config["AWS_ACCESS_KEY_ID"] = aws_access_key
    config["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
    config["AWS_DEFAULT_REGION"] = aws_region

    # Save the configuration for future runs.
    save_config(CONFIG_FILE, config)

    # Convert the backup paths string to a list.
    backup_paths = backup_paths_str.split()

    # Prepare environment variables for subprocess.
    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = aws_access_key
    env["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
    env["AWS_DEFAULT_REGION"] = aws_region

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

    subprocess.run(backup_cmd, check=True, env=env)

    # Check snapshots.
    print("Backup completed. Checking snapshots...")
    snapshots_cmd = [
        "sudo",
        "restic",
        "--repository-file", repo_file,
        "--password-file", pass_file,
        "snapshots",
    ]
    subprocess.run(snapshots_cmd, check=True, env=env)

    print("Restic backup and snapshot check complete.")


if __name__ == "__main__":
    main()
