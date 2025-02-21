#!/usr/bin/env python3
"""
check_restic_files.py

- Checks if /root/.restic-repo and /root/.restic-passwd exist.
- If a file doesn't exist, prompts for its contents and creates it.
- If a file exists, displays its contents and asks for confirmation.
- If the contents are not correct, updates the file with new contents provided by the user.
- Outputs what actions were performed.
- Prompts the user to then run ./createPersephoneConfig.py and exits.
"""

import os
import getpass

# Define file paths.
REPO_PATH = "/root/.restic-repo"
PASSWD_PATH = "/root/.restic-passwd"

def check_and_update_file(path, description, hidden=False):
    """
    Check if file exists and its contents are correct.
    If not, prompt the user for the correct contents and update the file.
    
    Returns the final contents of the file.
    """
    file_exists = os.path.exists(path)
    if file_exists:
        try:
            with open(path, "r") as f:
                current_content = f.read().strip()
        except Exception as e:
            print(f"Error reading {description} file at {path}: {e}")
            current_content = ""
        print(f"{description} file found at {path}.")
        print(f"Current contents: {current_content}")
        response = input(f"Is this correct? (Y/n): ").strip().lower()
        if response in ["", "y", "yes"]:
            print(f"No update needed for {description} file.")
            return current_content
        else:
            print(f"Updating {description} file...")
    else:
        print(f"{description} file not found at {path}. It will be created.")

    # Prompt for new content
    if hidden:
        new_content = getpass.getpass(f"Enter new contents for {description}: ").strip()
    else:
        new_content = input(f"Enter new contents for {description}: ").strip()
    try:
        with open(path, "w") as f:
            f.write(new_content + "\n")
        print(f"{description} file at {path} has been updated.")
    except Exception as e:
        print(f"Error writing to {description} file at {path}: {e}")
    return new_content

def main():
    print("Checking Restic repository and password files...\n")

    repo_content = check_and_update_file(REPO_PATH, "Restic repository")
    passwd_content = check_and_update_file(PASSWD_PATH, "Restic password", hidden=True)

    print("\nSummary of actions:")
    if repo_content:
        print(f"- {REPO_PATH} is set with: {repo_content}")
    else:
        print(f"- {REPO_PATH} is empty or not set correctly.")
    if passwd_content:
        print(f"- {PASSWD_PATH} is set (contents hidden).")
    else:
        print(f"- {PASSWD_PATH} is empty or not set correctly.")
    
    input("\nPlease run ./createPersephoneConfig.py to continue. Press Enter to exit.")
    
if __name__ == "__main__":
    main()
