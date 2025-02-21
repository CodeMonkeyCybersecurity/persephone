#!/usr/bin/env python3
"""
createPersephoneBackupS3.py

This script performs a Restic backup by prompting for required configuration
values—including AWS credentials—and storing those values in a config file 
(.persephone.conf) for future runs. It manages four key values:
  - PERS_REPO_FILE: The file path to the repository file.
  - PERS_REPO_FILE_VALUE: The literal content (e.g. a repository URL/spec) that should be in that file.
  - PERS_PASSWD_FILE: The file path to the password file.
  - PERS_PASSWD_FILE_VALUE: The literal password that should be in that file.
Before running the backup, the script updates those files with the confirmed values.
It then executes the Restic backup and snapshot commands.
"""

import os
import subprocess
import getpass

CONFIG_FILE = ".persephone.conf"

def load_config(config_file):
    """
    Loads configuration from the config file if it exists.
    Expected file format: one key="value" per line.
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
                    config[key.strip()] = value.strip().strip('"').strip("'")
    return config

def prompt_input(prompt_message, default_val=None, hidden=False):
    """
    Prompts the user for input with an optional default.
    If hidden=True, the input is hidden.
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

def get_confirmed_value(key, prompt_message, default_val, hidden=False):
    """
    Prompts for a value (e.g. a file path) and asks for confirmation.
    Returns the confirmed (or updated) value.
    """
    value = prompt_input(prompt_message, default_val, hidden)
    print(f"{key} is set to: {value}")
    answer = input("Is this correct? (Y/n): ").strip().lower()
    if answer in ["", "y", "yes"]:
        return value
    else:
        return prompt_input(f"Enter new value for {key}", default_val, hidden)

def save_config(config_file, config):
    """
    Saves the configuration dictionary to the config file.
    """
    with open(config_file, "w") as f:
        for key, value in config.items():
            f.write(f'{key}="{value}"\n')

def main():
    # Load existing configuration if available.
    config = load_config(CONFIG_FILE)

    print("=== Restic Backup Configuration ===")

    # --- Repository file and its value ---
    default_repo_file = config.get("PERS_REPO_FILE", "/root/.persephone-repo")
    pers_repo_file = get_confirmed_value("PERS_REPO_FILE", "Enter the repository file path", default_repo_file)
    
    default_repo_value = config.get("PERS_REPO_FILE_VALUE", "/root/.restic-password-content")
    pers_repo_file_value = get_confirmed_value("PERS_REPO_FILE_VALUE", "Enter the repository file literal value", default_repo_value)

    # --- Password file and its value ---
    default_pass_file = config.get("PERS_PASSWD_FILE", "/root/.persephone-passwd")
    pers_pass_file = get_confirmed_value("PERS_PASSWD_FILE", "Enter the password file path", default_pass_file)
    
    default_pass_value = config.get("PERS_PASSWD_FILE_VALUE", "/root/.restic-password-content")
    pers_pass_value = get_confirmed_value("PERS_PASSWD_FILE_VALUE", "Enter the password file literal value", default_pass_value, hidden=True)

    # --- Other configuration values ---
    default_backup_paths = config.get("BACKUP_PATHS_STR", "/root /home /var /etc /srv /usr /opt")
    backup_paths_str = prompt_input("Enter backup paths (space-separated)", default_backup_paths)

    default_aws_access_key = config.get("AWS_ACCESS_KEY_ID", "")
    aws_access_key = prompt_input("Enter AWS_ACCESS_KEY_ID", default_aws_access_key)

    default_aws_secret_key = config.get("AWS_SECRET_ACCESS_KEY", "")
    aws_secret_key = prompt_input("Enter AWS_SECRET_ACCESS_KEY", default_aws_secret_key, hidden=True)

    # Update configuration dictionary.
    config["PERS_REPO_FILE"] = pers_repo_file
    config["PERS_REPO_FILE_VALUE"] = pers_repo_file_value
    config["PERS_PASSWD_FILE"] = pers_pass_file
    config["PERS_PASSWD_FILE_VALUE"] = pers_pass_value
    config["BACKUP_PATHS_STR"] = backup_paths_str
    config["AWS_ACCESS_KEY_ID"] = aws_access_key
    config["AWS_SECRET_ACCESS_KEY"] = aws_secret_key

    # Save the configuration for future runs.
    save_config(CONFIG_FILE, config)
    print(f"\nConfiguration successfully saved to {CONFIG_FILE}")

    # Ensure the repository and password files on disk are updated with the literal values.
    try:
        with open(pers_repo_file, "w") as f:
            f.write(pers_repo_file_value + "\n")
        print(f"Updated repository file at {pers_repo_file} with the confirmed value.")
    except Exception as e:
        print(f"Error writing to {pers_repo_file}: {e}")
    
    try:
        with open(pers_pass_file, "w") as f:
            f.write(pers_pass_value + "\n")
        print(f"Updated password file at {pers_pass_file} with the confirmed value.")
    except Exception as e:
        print(f"Error writing to {pers_pass_file}: {e}")

    # Convert the backup paths string to a list.
    backup_paths = backup_paths_str.split()

    # Prepare environment variables for subprocess.
    env = os.environ.copy()
    env["AWS_ACCESS_KEY_ID"] = aws_access_key
    env["AWS_SECRET_ACCESS_KEY"] = aws_secret_key
  
    # Run the backup command.
    print("\nRunning Restic backup...")
    backup_cmd = [
        "sudo",
        "restic",
        "-r", pers_repo_file,
        "--password-file", pers_pass_file,
        "backup",
        "--verbose",
        "--tag",
        f"{os.uname().nodename}-$(date +\\%Y-\\%m-\\%d_\\%H-\\%M-\\%S)"
    ] + backup_paths

    subprocess.run(backup_cmd, check=True, env=env)

    # Check snapshots.
    print("Backup completed. Checking snapshots...")
    snapshots_cmd = [
        "sudo",
        "restic",
        "--repository-file", pers_repo_file,
        "--password-file", pers_pass_file,
        "snapshots"
    ]
    subprocess.run(snapshots_cmd, check=True, env=env)

    print("Restic backup and snapshot check complete.")

if __name__ == "__main__":
    main()
