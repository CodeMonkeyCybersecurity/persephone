import yaml
import logging
import paramiko
import os
from functools import wraps

# Configure logging
logging.basicConfig(filename="/var/log/cybermonkey/persephone_retrieve.log", level=logging.INFO,
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

# Retrieve files from remote host
@error_handler
def retrieve_files(target, dest_folder):
    host = target["host"]
    user = target["user"]
    ssh_key_path = target.get("ssh_key_path")
    files = target.get("files", ["/path/to/rpoKeys", "/path/to/config.yaml"])  # Define paths to retrieve

    # Set up SSH connection
    ssh = paramiko.SSHClient()
    ssh.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    ssh.connect(hostname=host, username=user, key_filename=ssh_key_path)

    sftp = ssh.open_sftp()

    for file in files:
        try:
            remote_file = file
            local_file = os.path.join(dest_folder, f"{host}_{os.path.basename(file)}")
            sftp.get(remote_file, local_file)
            logging.info(f"Retrieved {remote_file} from {host} to {local_file}")
        except Exception as e:
            logging.error(f"Failed to retrieve {file} from {host}: {e}")

    sftp.close()
    ssh.close()

# Main function to run retrievals sequentially
@error_handler
def perform_retrievals(config_path, dest_folder):
    config = load_config(config_path)
    backup_targets = config.get("backup_targets", [])
    
    for target in backup_targets:
        retrieve_files(target, dest_folder)

# Interactive menu
@error_handler
def display_menu():
    print("\n=== Persephone Configuration Retrieval ===")
    print("1. Retrieve configuration files from all clients")
    print("2. Retrieve configuration files from a specific client")
    print("3. Exit")
    choice = input("Choose an option: ")
    return choice

# Retrieve all configurations
@error_handler
def retrieve_all_configs(config_path, dest_folder):
    logging.info("Starting retrieval for all clients.")
    perform_retrievals(config_path, dest_folder)
    print("Retrieval for all clients completed.")

# Retrieve a specific configuration
@error_handler
def retrieve_specific_config(config_path, dest_folder):
    config = load_config(config_path)
    backup_targets = config.get("backup_targets", [])
    
    # Display clients for selection
    print("\nAvailable clients:")
    for i, target in enumerate(backup_targets):
        print(f"{i+1}. {target['name']} ({target['host']})")
    
    client_choice = int(input("Select a client by number: ")) - 1
    if 0 <= client_choice < len(backup_targets):
        target = backup_targets[client_choice]
        retrieve_files(target, dest_folder)
        print(f"Retrieved files from {target['name']} ({target['host']}).")
    else:
        print("Invalid choice.")

# Main execution with menu
def main():
    config_path = "/etc/CodeMonkeyCyber/Persephone/borgConfig.yaml"
    dest_folder = "/path/to/store/retrieved_files"  # Set your destination folder

    while True:
        choice = display_menu()
        
        if choice == "1":
            retrieve_all_configs(config_path, dest_folder)
        elif choice == "2":
            retrieve_specific_config(config_path, dest_folder)
        elif choice == "3":
            print("Exiting.")
            break
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
