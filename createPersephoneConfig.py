#!/usr/bin/env python3
"""
createPersephoneConfig.py

This script creates or updates the backup configuration file (.persephone.conf)
with values required by createPersephoneBackup.py.

It manages four key values:
  - PERS_REPO_FILE: The repository file path (e.g. /root/.persephone-repo)
  - PERS_REPO_FILE_VALUE: The literal value contained in that file
  - PERS_PASSWD_FILE: The password file path (e.g. /root/.persephone-passwd)
  - PERS_PASSWD_FILE_VALUE: The literal value contained in that file

For each, the script asks you to confirm the current setting. If you indicate it’s not
correct, you are prompted to update only the literal value (for the _VALUE keys) or the file path.
"""

import os
import shutil
import datetime
import getpass

CONFIG_FILE = ".persephone.conf"

def load_config(config_file):
    """
    Loads configuration from the file if it exists.
    Expected format: one key="value" per line.
    Returns a dictionary of configuration values.
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

def backup_existing_config(config_file):
    if os.path.exists(config_file):
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_file = f"{config_file}.{timestamp}.bak"
        shutil.copy2(config_file, backup_file)
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

def get_confirmed_value(key, prompt_message, default_val):
    """
    Prompts for a value with a default and asks for confirmation.
    Returns the confirmed (or updated) value.
    """
    value = prompt_input(prompt_message, default_val)
    print(f"{key} is set to: {value}")
    answer = input("Is this correct? (Y/n): ").strip().lower()
    if answer in ["", "y", "yes"]:
        return value
    else:
        return prompt_input(f"Enter new value for {key}", default_val)

def get_confirmed_file_value(file_path, description, hidden=False):
    """
    For a given file path, checks if the file exists.
      - If it exists, its content is read and displayed.
        You’re then asked to confirm that the content (the _VALUE) is correct.
        If not, you enter a new literal value and the file is overwritten.
      - If it does not exist, you are prompted for a literal value,
        and the file is created with that content.
    Returns the confirmed literal value.
    """
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                current_value = f.read().strip()
        except Exception as e:
            print(f"Error reading {description} file at {file_path}: {e}")
            current_value = ""
        print(f"{description} file found at '{file_path}' with content:\n  {current_value}")
        answer = input(f"Is this the correct value for {description}? (Y/n): ").strip().lower()
        if answer in ["", "y", "yes"]:
            return current_value
        else:
            new_value = prompt_input(f"Enter new literal value for {description}", current_value, hidden)
            try:
                with open(file_path, "w") as f:
                    f.write(new_value + "\n")
                print(f"Updated {description} file at {file_path}.")
            except Exception as e:
                print(f"Error updating {description} file at {file_path}: {e}")
            return new_value
    else:
        print(f"{description} file does not exist at {file_path}. It will be created.")
        new_value = prompt_input(f"Enter literal value for {description}", "", hidden)
        try:
            with open(file_path, "w") as f:
                f.write(new_value + "\n")
            print(f"Created {description} file at {file_path} with provided value.")
        except Exception as e:
            print(f"Error creating {description} file at {file_path}: {e}")
        return new_value

def main():
    # Load any existing configuration.
    existing_config = load_config(CONFIG_FILE)
    
    # --- For the repository file and its value ---
    default_repo_file = existing_config.get("PERS_REPO_FILE", "/root/.persephone-repo")
    pers_repo_file = get_confirmed_value("PERS_REPO_FILE", "Enter the repository file path", default_repo_file)
    
    pers_repo_file_value = get_confirmed_file_value(pers_repo_file, "PERS_REPO_FILE_VALUE", hidden=False)
    
    # --- For the password file and its value ---
    default_passwd_file = existing_config.get("PERS_PASSWD_FILE", "/root/.persephone-passwd")
    pers_passwd_file = get_confirmed_value("PERS_PASSWD_FILE", "Enter the password file path", default_passwd_file)
    
    pers_passwd_file_value = get_confirmed_file_value(pers_passwd_file, "PERS_PASSWD_FILE_VALUE", hidden=True)
    
    # --- Other configuration values ---
    backup_paths_str = existing_config.get("BACKUP_PATHS_STR") or prompt_input(
        "Enter backup paths (space-separated)", "/root /home /var /etc /srv /usr /opt")
    aws_access_key = existing_config.get("AWS_ACCESS_KEY_ID") or prompt_input("Enter AWS_ACCESS_KEY_ID", "")
    aws_secret_key = existing_config.get("AWS_SECRET_ACCESS_KEY") or prompt_input("Enter AWS_SECRET_ACCESS_KEY", "", hidden=True)
    
    # Back up existing config file.
    backup_existing_config(CONFIG_FILE)
    
    # Prepare configuration dictionary.
    config = {
        "PERS_REPO_FILE": pers_repo_file,
        "PERS_REPO_FILE_VALUE": pers_repo_file_value,
        "PERS_PASSWD_FILE": pers_passwd_file,
        "PERS_PASSWD_FILE_VALUE": pers_passwd_file_value,
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
