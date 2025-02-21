#!/usr/bin/env python3
"""
createPersephoneConfig.py

This script creates or updates the backup configuration file (.persephone_backup.conf)
with values required by createPersephoneBackup.py. If a configuration file already exists,
it backs it up (renaming it with a timestamp). The script prompts for the repository type
(s3, sftp, local, or rest) and then for the repository path and other configuration values.
"""

import os
import shutil
import datetime
import getpass

CONFIG_FILE = ".persephone_backup.conf"

def backup_existing_config(config_file):
    if os.path.exists(config_file):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{config_file}.{timestamp}.bak"
        shutil.move(config_file, backup_file)
        print(f"Existing config found. Backed up to: {backup_file}")

def prompt_input(prompt_message, default_val=None, hidden=False):
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

def choose_repo_type():
    repo_types = {
        "s3": "s3:https://s3api.cybermonkey.dev/restic",
        "sftp": "sftp:your_username@host:/path/to/repo",
        "local": "/path/to/local/repo",
        "rest": "rest:https://restserver.example.com/restic"
    }
    
    print("Select repository type:")
    for key in repo_types:
        print(f"  {key}")
    while True:
        choice = input("Enter repository type (s3/sftp/local/rest) [s3]: ").strip().lower()
        if choice == "":
            return "s3", repo_types["s3"]
        elif choice in repo_types:
            return choice, repo_types[choice]
        else:
            print("Invalid option. Please choose one of: s3, sftp, local, rest.")

def main():
    # Backup the existing config file if it exists.
    backup_existing_config(CONFIG_FILE)

    print("=== Persephone Backup Configuration ===")
    
    # Choose repository type and set default REPO_FILE value accordingly.
    repo_type, default_repo = choose_repo_type()
    repo_file = prompt_input("Enter the repository file/path", default_repo)
    
    # Prompt for remaining configuration values.
    pass_file = prompt_input("Enter the restic password file path", "/root/.restic-password")
    backup_paths_str = prompt_input("Enter backup paths (space-separated)", "/root /home /var /etc /srv /usr /opt")
    
    print("\n=== AWS Credentials ===")
    aws_access_key = prompt_input("Enter AWS_ACCESS_KEY_ID", "")
    aws_secret_key = prompt_input("Enter AWS_SECRET_ACCESS_KEY", "", hidden=True)
    
    # Prepare configuration dictionary.
    config = {
        "REPO_FILE": repo_file,
        "PASS_FILE": pass_file,
        "BACKUP_PATHS_STR": backup_paths_str,
        "AWS_ACCESS_KEY_ID": aws_access_key,
        "AWS_SECRET_ACCESS_KEY": aws_secret_key
    }
    
    # Write configuration to file.
    try:
        with open(CONFIG_FILE, "w") as f:
            for key, value in config.items():
                f.write(f'{key}="{value}"\n')
        print(f"\nConfiguration successfully saved to {CONFIG_FILE}")
    except Exception as e:
        print(f"Error saving configuration: {e}")

if __name__ == "__main__":
    main()
