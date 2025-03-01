#!/usr/bin/env python3
"""
prune.py

This script performs a restic prune operation using configuration defaults stored
in ~/.prune_defaults. It prompts for:
  - Backup server user (PERS_USER)
  - Backup server hostname (PERS_HOSTN)
  - Number of hourly snapshots to keep (HR)
  - Number of daily snapshots to keep (DY)
  - Number of weekly snapshots to keep (WK)
  - Number of monthly snapshots to keep (MN)
  - Number of yearly snapshots to keep (YR)
  - Number of most recent snapshots to keep (LT)

The script then executes the restic command using these values and saves the
current settings back to ~/.prune_defaults for future runs.
"""

import os
import subprocess
import socket

CONFIG_FILE = ".persephone.conf"

def load_config(config_file):
    """
    Loads configuration from the given config file.
    Expected file format (one key="value" per line).
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

def prompt_input(prompt_message, default_val=""):
    """
    Prompts the user for input using an optional default value.
    """
    if default_val:
        prompt = f"{prompt_message} [{default_val}]: "
    else:
        prompt = f"{prompt_message}: "
    response = input(prompt).strip()
    return response if response else default_val

def save_config(config_file, config):
    """
    Saves the configuration dictionary to the given config file.
    """
    with open(config_file, "w") as f:
        for key, value in config.items():
            f.write(f'{key}="{value}"\n')

def main():
    # Load previous configuration if available.
    config = load_config(CONFIG_FILE)
    
    # Prompt for values (using previously stored values as defaults if they exist).
    pers_user = prompt_input("What user on the backup server do you need to connect to?", config.get("PERS_USER", ""))
    pers_hostn = prompt_input("What hostname on the backup server do you need to connect to?", config.get("PERS_HOSTN", ""))
    hr = prompt_input("How many hourly snapshots should be kept?", config.get("HR", ""))
    dy = prompt_input("How many daily snapshots should be kept?", config.get("DY", ""))
    wk = prompt_input("How many weekly snapshots should be kept?", config.get("WK", ""))
    mn = prompt_input("How many monthly snapshots should be kept?", config.get("MN", ""))
    yr = prompt_input("How many yearly snapshots should be kept?", config.get("YR", ""))
    lt = prompt_input("How many of the most recent snapshots should be kept?", config.get("LT", ""))
    
    # Construct the restic repository string.
    # The repository is of the form:
    #   sftp:PERS_USER@PERS_HOSTN:/srv/restic-repos/<local_hostname>
    local_hostname = socket.gethostname()
    repo = f"sftp:{pers_user}@{pers_hostn}:/srv/restic-repos/{local_hostname}"
    
    # Build the restic command.
    restic_cmd = [
        "sudo", "restic",
        "-r", repo,
        "--password-file", "/root/.restic-password",
        "forget", "--prune",
        "--keep-hourly", hr,
        "--keep-daily", dy,
        "--keep-weekly", wk,
        "--keep-monthly", mn,
        "--keep-yearly", yr,
        "--keep-last", lt
    ]
    
    # Execute the restic command.
    try:
        subprocess.run(restic_cmd, check=True)
        print("Restic prune operation completed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error running restic command:", e)
        return

    # Save the current settings to the configuration file.
    config.update({
        "PERS_USER": pers_user,
        "PERS_HOSTN": pers_hostn,
        "HR": hr,
        "DY": dy,
        "WK": wk,
        "MN": mn,
        "YR": yr,
        "LT": lt
    })
    save_config(CONFIG_FILE, config)
    print(f"Configuration saved to {CONFIG_FILE}")

if __name__ == "__main__":
    main()
