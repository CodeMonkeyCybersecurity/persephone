import yaml
import subprocess
import os

# Path to the config file
CONFIG_FILE = '/etc/CodeMonkeyCyber/Persephone/borgConfig.yaml'

# Load configuration
def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return yaml.safe_load(file)

# Export Borg encryption key
def export_borg_key():
    config = load_config()

    # Extract repository path and passphrase from config
    repo = config['borg'].get('repo')
    passphrase = config['borg'].get('passphrase', '')

    # Specify the default key export path
    default_key_path = os.path.expanduser(f"~/borg_keys/{repo.split('/')[-1]}_key.borg")
    export_path = input(f"Enter export path (default: {default_key_path}): ").strip() or default_key_path

    # Ensure the export directory exists
    os.makedirs(os.path.dirname(export_path), exist_ok=True)

    # Construct borg key export command
    cmd = [
        "borg", "key", "export",
        repo,
        export_path
    ]

    # Export passphrase environment variable
    env = os.environ.copy()
    env["BORG_PASSPHRASE"] = passphrase

    # Execute the export command
    try:
        subprocess.run(cmd, env=env, check=True)
        print(f"Borg encryption key exported successfully to {export_path}")
    except subprocess.CalledProcessError as e:
        print("Error exporting encryption key:", e)

# Run the export function
if __name__ == "__main__":
    export_borg_key()
