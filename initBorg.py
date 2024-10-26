import yaml
import subprocess
import os

# Path to the config file
CONFIG_FILE = '/etc/CodeMonkeyCyber/Persephone/borgConfig.yaml'

# Load configuration
def load_config():
    with open(CONFIG_FILE, 'r') as file:
        return yaml.safe_load(file)

# Initialize borg repository based on config values
def init_borg_repo():
    config = load_config()

    # Extract repository and encryption settings
    repo = config['borg'].get('repo')
    encryption = config['borg'].get('encryption', 'repokey')
    passphrase = config['borg'].get('passphrase', '')
    rsh = config['borg'].get('rsh', 'ssh')

    # Construct borg init command
    cmd = [
        "borg", "init",
        f"--encryption={encryption}",
        "--rsh", rsh,
        repo
    ]

    # Export passphrase environment variable
    env = os.environ.copy()
    env["BORG_PASSPHRASE"] = passphrase

    # Confirm if reinitializing an existing repo
    print(f"Initializing Borg repository at {repo} with encryption: {encryption}")
    user_confirm = input("Proceed with initialization? (This will overwrite if repo exists) [y/N]: ").strip().lower()
    if user_confirm != 'y':
        print("Initialization aborted.")
        return

    # Run the borg init command
    try:
        subprocess.run(cmd, env=env, check=True)
        print("Borg repository initialized successfully.")
    except subprocess.CalledProcessError as e:
        print("Error initializing repository:", e)

# Run the init function
if __name__ == "__main__":
    init_borg_repo()
