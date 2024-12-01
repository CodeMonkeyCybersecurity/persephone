# Load the YAML configuration
def create_yaml_config():
    """Create the YAML config file at /etc/eos/borg_config.yaml with default values."""
    # Default values for the configuration
    default_repo = "henry@ubuntu-backups:/mnt/cybermonkey"
    default_passphrase = "Linseed7)Twine33Phoney57Barracuda4)Province0"
    default_encryption = "repokey"
    default_paths_to_backup = "/var,/etc,/home,/root,/opt,/mnt"
    default_exclude_patterns = "home/*/.cache/*,var/tmp/*"
    default_compression = "zstd"

    # Prompt the user for inputs, with default values suggested
    config = {
        'borg': {
            'repo': input(f"Enter the Borg repository path (default: {default_repo}): ") or default_repo,
            'passphrase': input(f"Enter the Borg passphrase (default: {default_passphrase}): ") or default_passphrase,
            'encryption': input(f"Enter the encryption type (e.g., repokey, none, default: {default_encryption}): ") or default_encryption
        },
        'backup': {
            'paths_to_backup': input(f"Enter the directories to back up (comma-separated, default: {default_paths_to_backup}): ") or default_paths_to_backup,
            'exclude_patterns': input(f"Enter exclude patterns (comma-separated, default: {default_exclude_patterns}): ") or default_exclude_patterns,
            'compression': input(f"Enter the compression method (e.g., lz4, zstd, default: {default_compression}): ") or default_compression
        }
    }

    # Save to YAML
    try:
        os.makedirs(os.path.dirname(CONFIG_PATH), exist_ok=True)
        with open(CONFIG_PATH, 'w') as file:
            yaml.safe_dump(config, file)
        logging.info(f"Configuration saved to {CONFIG_PATH}.")
    except OSError as e:
        logging.error(f"Failed to write the configuration file: {e}")

def load_config():
    """Load configuration from YAML file."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as file:
                config = yaml.safe_load(file)
                logging.info("Configuration loaded successfully.")
                return config
        except yaml.YAMLError as e:
            logging.error(f"Error loading configuration file: {e}")
            return None
    else:
        logging.error(f"Configuration file not found.")
        return None
