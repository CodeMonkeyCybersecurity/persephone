import yaml
import os
import logging

# Paths
CONFIG_FILE = '/etc/CodeMonkeyCyber/Persephone/borgConfig.yaml'
LOG_DIR = '/var/log/CodeMonkeyCyber'
LOG_FILE = f'{LOG_DIR}/Persephone.log'
SUBMODULES_SOURCE = './submodules'
SUBMODULES_DEST = '/usr/local/bin/Persephone'

from utils.checkSudo import check_sudo

# Default configuration template
default_config = {
    'borg': {
        'repo': 'username@hostname:/mnt/default',
        'encryption': 'repokey',
        'passphrase': 'YourSecurePassphrase',
        'rsh': 'ssh -i /path/to/id_ed25519'
    },
    'backup': {
        'compression': 'zstd',
        'exclude_patterns': [
            'home/*/.cache/*',
            'var/tmp/*'
        ],
        'paths_to_backup': [
            '/var',
            '/etc',
            '/home',
            '/root',
            '/opt',
            '/mnt',
            '/usr'
        ],
        'prune': {
            'daily': 7,
            'weekly': 4,
            'monthly': 6,
            'yearly': 1
        }
    }
}

# Ensure log directory exists
os.makedirs(LOG_DIR, exist_ok=True)

# Configure logging
logging.basicConfig(filename=LOG_FILE, level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

# Load or create configuration
def load_config():
    # Check if the config file exists
    if not os.path.exists(CONFIG_FILE):
        print(f"Configuration file not found at {CONFIG_FILE}. Creating with default settings.")
        os.makedirs(os.path.dirname(CONFIG_FILE), exist_ok=True)
        
        # Write the default configuration to the file
        with open(CONFIG_FILE, 'w') as file:
            yaml.dump(default_config, file)
        print(f"Default configuration created at {CONFIG_FILE}. Please review and update as needed.")

    # Load the configuration
    with open(CONFIG_FILE, 'r') as file:
        return yaml.safe_load(file)

# Example function that uses the config
def init_borg_repo():
    config = load_config()
    logging.info("Configuration loaded successfully.")
    # Rest of your function here

# Main function to run the script
def main():
    checkSudo()
    load_config()
    init_borg_repo()

# Run main() if the script is executed directly
if __name__ == "__main__":
    main()
