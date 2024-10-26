import yaml
import subprocess
import os
from datetime import datetime

# Path to the config file
CONFIG_FILE = '/etc/CodeMonkeyCyber/Persephone/borgConfig.yaml'

# Load configuration
def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return yaml.safe_load(file)

# Generate borg create command based on config values
def create_borg_command():
    config = load_config()

    # Extract values from config
    repo = config['borg'].get('repo')
    compression = config['backup'].get('compression', 'none')
    encryption = config['borg'].get('encryption', 'none')
    passphrase = config['borg'].get('passphrase', '')
    rsh = config['borg'].get('rsh', 'ssh')
    paths_to_backup = config['backup'].get('paths_to_backup', [])
    exclude_patterns = config['backup'].get('exclude_patterns', [])

    # Generate archive name with date, time, and size
    archive_name = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')

    # Construct borg command
    cmd = [
        "borg", "create",
        f"--compression={compression}",
        f"--rsh={rsh}",
        f"{repo}::{archive_name}"
    ]

    # Add paths to backup
    cmd.extend(paths_to_backup)

    # Add exclude patterns
    for pattern in exclude_patterns:
        cmd.extend(["--exclude", pattern])

    # Export passphrase environment variable
    env = os.environ.copy()
    env["BORG_PASSPHRASE"] = passphrase

    # Print the constructed command
    print("Constructed borg command:", " ".join(cmd))

    # Run the borg create command (uncomment to enable execution)
    subprocess.run(cmd, env=env)

# Run the function
create_borg_command()
