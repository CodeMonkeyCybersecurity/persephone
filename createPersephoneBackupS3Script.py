#!/usr/bin/env python3
"""
createPersephoneBackupS3Script.py

This script performs a Restic backup by prompting for required configuration
values—including AWS credentials—and storing those values in a config file 
(.persephone.conf) for future runs. It manages four key values:
  - PERS_REPO_FILE: The file path to the repository file.
  - PERS_REPO_FILE_VALUE: The literal content (e.g. a repository URL/spec) that should be in that file.
  - PERS_PASSWD_FILE: The file path to the password file.
  - PERS_PASSWD_FILE_VALUE: The literal password that should be in that file.
Before running the backup, the script updates those files with the confirmed values.
Instead of directly running the backup, it outputs a minimal bash script in the format:

    #!/bin/bash
    export AWS_ACCESS_KEY_ID=<value>
    export AWS_SECRET_ACCESS_KEY=<value>
    restic -r <PERS_REPO_FILE_VALUE> --password-file <PERS_PASSWD_FILE> backup --verbose <backup_paths> --tag "<hostname>-$(date +\\%Y-\\%m-\\%d_\\%H-\\%M-\\%S)"
    echo ""
    echo "finis"

It then makes the script executable, creates /opt/persephone/ if needed, and moves the bash script there.
"""

import os
import subprocess
import getpass
import socket
import shutil

CONFIG_FILE = ".persephone.conf"
BASH_SCRIPT_NAME = "persephone.sh"
TARGET_DIR = "/opt/persephone/"

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
    Prompts for a value (e.g. a file path or literal value) and asks for confirmation.
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

def generate_bash_script(config):
    """
    Generates a minimal bash script (persephone.sh) using the configuration values.
    """
    hostname = socket.gethostname()
    # Build the restic command using the literal repository value and backup paths.
    bash_lines = [
        "#!/bin/bash",
        "",
        f"export AWS_ACCESS_KEY_ID={config['AWS_ACCESS_KEY_ID']}",
        f"export AWS_SECRET_ACCESS_KEY={config['AWS_SECRET_ACCESS_KEY']}",
        # Construct the restic backup command.
        f"restic -r {config['PERS_REPO_FILE_VALUE']} --password-file {config['PERS_PASSWD_FILE']} backup --verbose {config['BACKUP_PATHS_STR']} --tag \"{hostname}-$(date +\\%Y-\\%m-\\%d_\\%H-\\%M-\\%S)\"",
        "echo \"\"",
        "echo \"finis\""
    ]
    return "\n".join(bash_lines)

def main():
    # Load existing configuration if available.
    config = load_config(CONFIG_FILE)

    print("=== Restic Backup Configuration ===")

    # --- Repository file and its value ---
    default_repo_file = config.get("PERS_REPO_FILE", "/root/.persephone-repo")
    pers_repo_file = get_confirmed_value("PERS_REPO_FILE", "Enter the repository file path", default_repo_file)
    
    default_repo_value = config.get("PERS_REPO_FILE_VALUE", "s3:https://persephoneapi.domain.com/repo-name/endpoint-name")
    pers_repo_file_value = get_confirmed_value("PERS_REPO_FILE_VALUE", "Enter the repository file literal value", default_repo_value)

    # --- Password file and its value ---
    default_pass_file = config.get("PERS_PASSWD_FILE", "/root/.persephone-passwd")
    pers_pass_file = get_confirmed_value("PERS_PASSWD_FILE", "Enter the password file path", default_pass_file)
    
    default_pass_value = config.get("PERS_PASSWD_FILE_VALUE", "default-password")
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

    # Generate the minimal bash script.
    bash_script = generate_bash_script(config)
    script_path = os.path.join(os.getcwd(), BASH_SCRIPT_NAME)
    try:
        with open(script_path, "w") as f:
            f.write(bash_script + "\n")
        # Make it executable.
        os.chmod(script_path, 0o755)
        print(f"\nBash script '{BASH_SCRIPT_NAME}' generated in current directory.")
    except Exception as e:
        print(f"Error writing bash script: {e}")
        return

    # Create target directory if it doesn't exist and move the script there.
    try:
        os.makedirs(TARGET_DIR, exist_ok=True)
        target_path = os.path.join(TARGET_DIR, BASH_SCRIPT_NAME)
        shutil.move(script_path, target_path)
        print(f"Bash script moved to: {target_path}.") 
        print("")
        print("Please now run /opt/persephone/persephone.sh to check it works correctly.")
        print("")
        print("If it does work correctly, then please consider running ./createPersephoneSchedule.py to implement automated regular backups.")
    except Exception as e:
        print(f"Error moving bash script to {TARGET_DIR}: {e}")

if __name__ == "__main__":
    main()
