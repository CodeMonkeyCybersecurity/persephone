#!/usr/bin/env python3
"""
createPersephoneConfig.py

This script creates or updates the backup configuration file (.persephone.conf)
with values required by createPersephoneBackup.py.

For the repository and password settings, you can either supply the literal values
or a path to a file that contains the desired value. If a file exists at the given path,
the script reads its contents, shows them to you, and asks for confirmation.
If you do not confirm, you can enter the literal value instead.
"""

import os
import shutil
import datetime
import getpass

CONFIG_FILE = ".persephone.conf"

def load_config(config_file):
    """
    Loads configuration from the config file if it exists.
    Expected file format (one key="value" per line).
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
                    value = value.strip().strip('"').strip("'")
                    config[key] = value
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

def choose_repo_type(existing_value=None):
    repo_types = {
        "s3": "/root/.restic-repo",
        "sftp": "/root/.restic-repo",
        "local": "/root/.restic-repo",
        "rest": "/root/.restic-repo"
    }
    
    print("Select repository type:")
    for key in repo_types:
        print(f"  {key}")
    
    # Try to infer default choice from an existing value.
    default_choice = "s3"
    if existing_value:
        for typ in repo_types:
            if existing_value.startswith(typ + ":") or (typ == "local" and existing_value.startswith("/")):
                default_choice = typ
                break
                
    while True:
        choice = input(f"Enter repository type (s3/sftp/local/rest) [{default_choice}]: ").strip().lower()
        if choice == "":
            choice = default_choice
        if choice in repo_types:
            return choice, repo_types[choice]
        else:
            print("Invalid option. Please choose one of: s3, sftp, local, rest.")

def get_value_from_file_or_input(key, prompt_message, default_val, hidden=False):
    """
    Prompts for a value that may either be a literal value or a file path.
    If the entered value is a path to an existing file, its contents are read
    and displayed for confirmation. If confirmed, the file content is returned;
    otherwise, the user is prompted to enter a literal value.
    """
    value_input = prompt_input(prompt_message, default_val, hidden)
    if os.path.exists(value_input):
        try:
            with open(value_input, 'r') as f:
                file_content = f.read().strip()
            print(f"Found file at '{value_input}' with content:\n  {file_content}")
            answer = input(f"Is this the correct value for {key}? (Y/n): ").strip().lower()
            if answer in ["", "y", "yes"]:
                return file_content
            else:
                return prompt_input(f"Enter literal value for {key}", default_val, hidden)
        except Exception as e:
            print(f"Error reading file {value_input}: {e}")
            return prompt_input(f"Enter literal value for {key}", default_val, hidden)
    else:
        return value_input

def main():
    # Load previous configuration if available.
    existing_config = load_config(CONFIG_FILE)
    
    # For REPO_FILE: prompt for a value (or file path) and, if a file is provided,
    # read its contents.
    if "REPO_FILE" in existing_config:
        repo_default = existing_config["REPO_FILE"]
        print(f"Existing REPO_FILE value: {repo_default}")
    else:
        # Let the user choose repository type and use its default value.
        repo_type, repo_type_default = choose_repo_type()
        repo_default = repo_type_default
    
    repo_value = get_value_from_file_or_input("REPO_FILE", 
                                              "Enter the repository value or file path", 
                                              repo_default)
    
    # For PASS_FILE: similarly prompt for a value (or file path) and read contents if applicable.
    if "PASS_FILE" in existing_config:
        pass_default = existing_config["PASS_FILE"]
        print(f"Existing PASS_FILE value: {pass_default}")
    else:
        pass_default = "/root/.restic-password"
        
    pass_value = get_value_from_file_or_input("PASS_FILE", 
                                              "Enter the restic password value or file path", 
                                              pass_default, 
                                              hidden=True)
    
    # Prompt for remaining configuration values.
    backup_paths_str = existing_config.get("BACKUP_PATHS_STR") or prompt_input(
        "Enter backup paths (space-separated)", "/root /home /var /etc /srv /usr /opt")
    
    aws_access_key = existing_config.get("AWS_ACCESS_KEY_ID") or prompt_input("Enter AWS_ACCESS_KEY_ID", "")
    
    aws_secret_key = existing_config.get("AWS_SECRET_ACCESS_KEY") or prompt_input("Enter AWS_SECRET_ACCESS_KEY", "", hidden=True)
    
    # Back up the existing config file if it exists.
    backup_existing_config(CONFIG_FILE)
    
    # Prepare configuration dictionary.
    config = {
        "REPO_FILE": repo_value,
        "PASS_FILE": pass_value,
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
