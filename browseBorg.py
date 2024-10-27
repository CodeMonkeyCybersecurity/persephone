import os
import subprocess
import yaml

# Path to the YAML configuration file
CONFIG_FILE_PATH = "/etc/CodeMonkeyCyber/Persephone/borgConfig.yaml"  # Adjust if needed

def load_config():
    """Load Borg configuration from YAML file."""
    with open(CONFIG_FILE_PATH, "r") as file:
        config = yaml.safe_load(file)
    return config

def list_archives(repo_path):
    """List all archives in the specified Borg repository."""
    print("Listing all archives in the repository...")
    result = subprocess.run(["borg", "list", repo_path], capture_output=True, text=True)
    print(result.stdout)

def show_archive_details(repo_path, archive_name):
    """Show details of a specific archive in the repository."""
    print(f"Showing details for archive: {archive_name}")
    result = subprocess.run(["borg", "info", f"{repo_path}::{archive_name}"], capture_output=True, text=True)
    print(result.stdout)

def extract_from_archive(repo_path, archive_name, extract_path, file_path=None):
    """
    Extract files or directories from a specified archive.
    - archive_name: Name of the archive to extract from
    - extract_path: Path where the files will be extracted
    - file_path: Optional specific file or directory path to extract
    """
    borg_command = ["borg", "extract", f"{repo_path}::{archive_name}"]
    if file_path:
        borg_command.append(file_path)
    print(f"Extracting from archive: {archive_name} to {extract_path}")
    os.makedirs(extract_path, exist_ok=True)
    subprocess.run(borg_command, cwd=extract_path)

def main():
    # Load configuration
    config = load_config()
    repo_path = config.get("borg", {}).get("repo")

    if not repo_path:
        print("Repository path not found in configuration file.")
        return

    print("Borg Archive Navigation Tool")
    while True:
        print("\nOptions:")
        print("1. List all archives")
        print("2. Show details of an archive")
        print("3. Extract files from an archive")
        print("4. Exit")

        choice = input("Select an option (1-4): ")
        
        if choice == "1":
            list_archives()
        
        elif choice == "2":
            archive_name = input("Enter the archive name: ")
            show_archive_details(, archive_name)
        
        elif choice == "3":
            archive_name = input("Enter the archive name: ")
            extract_path = input("Enter the destination path for extraction: ")
            file_path = input("Enter the specific file or directory path to extract (leave blank for full archive): ")
            extract_from_archive(, archive_name, extract_path, file_path if file_path else None)
        
        elif choice == "4":
            print("Exiting.")
            break
        
        else:
            print("Invalid option. Please try again.")

if __name__ == "__main__":
    main()
