import yaml
import os
import subprocess
import logging
from datetime import datetime
import socket  # Used to get the hostname

#main function
def main():
    while True:
        clear_screen()
        display_menu()
        choice = input("Select an option: ").upper()

        if choice == 'C':
            config = load_config()
            if config:
                add_borg_to_crontab(config)
            else:
                print("Error: No valid configuration found.")
        elif choice == 'M':
            print("Showing the main menu...")
            logging.info("Showing the main menu.")
            continue  # Show the menu again
        elif choice == 'H':
            print("Help: This is a Borg Backup tool for managing backups and repositories.")
        elif choice == 'N':  # Run backup immediately
            print("Validating configuration for backup...")
            config = load_config()  # Ensure config is loaded
            if config:
                logging.info("Configuration validated successfully.")
                print("Running backup now...")
                run_borg_backup(config)  # Run the backup
            else:
                logging.error("No valid configuration found. Unable to run backup.")
                print("Error: No valid configuration found.")
        elif choice == 'O':  # Repository options menu
            print("Opening repository options menu...")
            repository_options_menu()  # Correctly call repository options menu
        elif choice in ['Y', 'B', 'R', 'D', 'A']:
            while True:
                display_submenu()
                submenu_choice = input("Select an option: ").upper()
                if submenu_choice == 'M':
                    break  # Return to the main menu
                else:
                    handle_submenu_option(submenu_choice)
        elif choice == 'E':
            print("Exiting program...")
            exit_program()
        else:
            print("Invalid choice. Please try again.")

if __name__ == "__main__":
    main()
