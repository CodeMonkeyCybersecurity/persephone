import yaml
import subprocess
import socket
import logging
import os
from datetime import datetime


# Define the log file and directory
LOG_DIR = '/var/log/CodeMonkeyCyber'
LOG_FILE = f'{LOG_DIR}/Persephone.log'

# Ensure the log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Path to the config file
CONFIG_FILE = '/etc/CodeMonkeyCyber/Persephone/borgConfig.yaml'

# Load configuration from YAML file
def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return yaml.safe_load(file)

# Prompt the user for settings
def get_user_input():
    config = {
        'borg': {
            'repo': input("Enter the Borg repository path (e.g., henry@ubuntu-backups:/mnt/2TB/ubuntu-redfern): ").strip(),
            'encryption': input("Enter encryption method (e.g., repokey): ").strip(),
            'passphrase': input("Enter your encryption passphrase: ").strip(),
            'rsh': input("Enter the remote shell command (e.g., ssh -i /path/to/id_ed25519): ").strip()
        },
        'backup': {
            'compression': input("Enter compression method (e.g., zstd): ").strip(),
            'exclude_patterns': [
                input("Enter exclude pattern 1 (e.g., home/*/.cache/*): ").strip(),
                input("Enter exclude pattern 2 (e.g., var/tmp/*): ").strip()
            ],
            'paths_to_backup': [
                input("Enter path to backup 1 (e.g., /var): ").strip(),
                input("Enter path to backup 2 (e.g., /etc): ").strip(),
                input("Enter path to backup 3 (e.g., /home): ").strip(),
                input("Enter path to backup 4 (e.g., /root): ").strip(),
                input("Enter path to backup 5 (e.g., /opt): ").strip(),
                input("Enter path to backup 6 (e.g., /mnt): ").strip(),
                input("Enter path to backup 7 (e.g., /usr): ").strip()
            ],
            'prune': {
                'daily': int(input("Enter number of daily backups to keep: ").strip()),
                'weekly': int(input("Enter number of weekly backups to keep: ").strip()),
                'monthly': int(input("Enter number of monthly backups to keep: ").strip()),
                'yearly': int(input("Enter number of yearly backups to keep: ").strip())
            }
        }
    }
    return config

# Create and save the YAML file
def create_yaml_file():
    config = get_user_input()
    
    with open(CONFIG_FILE, 'w') as file:
        yaml.dump(config, file)
    
    print(f"Configuration file created successfully at {CONFIG_FILE}. Please review and update as needed.")

# Main function
if __name__ == "__main__":
    create_yaml_file()
