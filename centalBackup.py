import yaml
import subprocess
import logging
from datetime import datetime
from functools import wraps
import paramiko

# Configure logging
logging.basicConfig(filename="/var/log/cybermonkey/persephone.log", level=logging.INFO,
                    format="%(asctime)s - %(levelname)s - %(message)s")

# Error handling decorator
def error_handler(func):
    @wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            logging.error(f"Error in {func.__name__}: {e}")
            raise e
    return wrapper

# Load YAML configuration
@error_handler
def load_config(file_path):
    with open(file_path, "r") as file:
        return yaml.safe_load(file)

# Run Borg backup command over SSH
@error_handler
def run_backup(target):
    name = target["name"]
    host = target["host"]
    user = target["user"]
    paths = " ".join(target["paths"])
    repo_path = target["repo_path"]
    ssh_key_path = target.get("ssh_key_path")
    compression = target.get("compression", "lz4")
    exclude_patterns = target.get("exclude_patterns", [])

    # Prepare exclude options
    exclude_options = " ".join([f"--exclude {pattern}" for pattern in exclude_patterns])
    borg_cmd = f"borg create --compression {compression} {exclude_options} {repo_path}::'{datetime.now().isoformat()}' {paths}"

    logging.info(f"Starting backup for {name} on {host}...")

    # Set up SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=user, key_filename=ssh_key_path)

    # Run the Borg command
    stdin, stdout, stderr = ssh.exec_command(borg_cmd)
    exit_status = stdout.channel.recv_exit_status()
    if exit_status == 0:
        logging.info(f"Backup for {name} on {host} completed successfully.")
    else:
        error_message = stderr.read().decode()
        logging.error(f"Backup for {name} on {host} failed: {error_message}")

    ssh.close()

# Main function to run backups sequentially
@error_handler
def perform_backups(config_path):
    config = load_config(config_path)
    backup_targets = config.get("backup_targets", [])
    
    for target in backup_targets:
        run_backup(target)  # Run each backup sequentially

if __name__ == "__main__":
    # Path to your configuration file
    config_path = "/etc/CodeMonkeyCyber/Persephone/borgConfig.yaml"
    perform_backups(config_path)
