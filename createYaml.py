import yaml
import os
import logging

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
    if os.path.exists(CONFIG_FILE):
        with open(CONFIG_FILE, 'r') as file:
            return yaml.safe_load(file)
    return {}  # Return an empty dictionary if the config file doesn't exist

# Prompt the user for settings, displaying defaults if available
def get_user_input():
    current_config = load_config()

    def prompt_with_default(prompt_text, default_value):
        """Prompt the user with a default value if available."""
        if default_value:
            return input(f"{prompt_text} (default: {default_value}): ").strip() or default_value
        return input(f"{prompt_text}: ").strip()

    config = {
        'borg': {
            'repo': prompt_with_default("Enter the Borg repository path", current_config.get('borg', {}).get('repo')),
            'encryption': prompt_with_default("Enter encryption method", current_config.get('borg', {}).get('encryption')),
            'passphrase': prompt_with_default("Enter your encryption passphrase", current_config.get('borg', {}).get('passphrase')),
            'rsh': prompt_with_default("Enter the remote shell command", current_config.get('borg', {}).get('rsh'))
        },
        'backup': {
            'compression': prompt_with_default("Enter compression method", current_config.get('backup', {}).get('compression')),
            'exclude_patterns': [
                prompt_with_default("Enter exclude pattern 1", current_config.get('backup', {}).get('exclude_patterns', [])[0] if len(current_config.get('backup', {}).get('exclude_patterns', [])) > 0 else ""),
                prompt_with_default("Enter exclude pattern 2", current_config.get('backup', {}).get('exclude_patterns', [])[1] if len(current_config.get('backup', {}).get('exclude_patterns', [])) > 1 else "")
            ],
            'paths_to_backup': [
                prompt_with_default("Enter path to backup 1", current_config.get('backup', {}).get('paths_to_backup', [])[0] if len(current_config.get('backup', {}).get('paths_to_backup', [])) > 0 else ""),
                prompt_with_default("Enter path to backup 2", current_config.get('backup', {}).get('paths_to_backup', [])[1] if len(current_config.get('backup', {}).get('paths_to_backup', [])) > 1 else ""),
                prompt_with_default("Enter path to backup 3", current_config.get('backup', {}).get('paths_to_backup', [])[2] if len(current_config.get('backup', {}).get('paths_to_backup', [])) > 2 else ""),
                prompt_with_default("Enter path to backup 4", current_config.get('backup', {}).get('paths_to_backup', [])[3] if len(current_config.get('backup', {}).get('paths_to_backup', [])) > 3 else ""),
                prompt_with_default("Enter path to backup 5", current_config.get('backup', {}).get('paths_to_backup', [])[4] if len(current_config.get('backup', {}).get('paths_to_backup', [])) > 4 else ""),
                prompt_with_default("Enter path to backup 6", current_config.get('backup', {}).get('paths_to_backup', [])[5] if len(current_config.get('backup', {}).get('paths_to_backup', [])) > 5 else ""),
                prompt_with_default("Enter path to backup 7", current_config.get('backup', {}).get('paths_to_backup', [])[6] if len(current_config.get('backup', {}).get('paths_to_backup', [])) > 6 else "")
            ],
            'prune': {
                'daily': int(prompt_with_default("Enter number of daily backups to keep", current_config.get('backup', {}).get('prune', {}).get('daily', ''))),
                'weekly': int(prompt_with_default("Enter number of weekly backups to keep", current_config.get('backup', {}).get('prune', {}).get('weekly', ''))),
                'monthly': int(prompt_with_default("Enter number of monthly backups to keep", current_config.get('backup', {}).get('prune', {}).get('monthly', ''))),
                'yearly': int(prompt_with_default("Enter number of yearly backups to keep", current_config.get('backup', {}).get('prune', {}).get('yearly', '')))
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
