# Edit YAML menu
def editYamlMenu(config):
    """Display YAML editing options."""
    while True:
        print("\nEditing existing YAML file. What would you like to edit?")
        print("(0) Compression method (eg. lz4, zstd. Default is zstd)")
        print("(1) Enter the encryption type (e.g., repokey, none)")
        print("(2) Borg repository path (e.g., user@backup-server:/path/to/repo. You must make sure this exists and is available prior to running a backup)")
        print("(3) Enter the directories to back up (comma-separated, default is: /etc,/var,/home,/mnt,/root,/opt)")
        print("(4) Enter exclude patterns (comma-separated, default is: home/*/.cache/*,var/tmp/*)")
        print("(5) Prune settings (comma-separated in format d,w,m,y. Default is 30,0,0,0)")
        print("(6) Edit with nano")
        print("(7) Return to main Menu")
        print("(E) (E)xit")
        
        choice = input("Select an option: ").upper()

        if choice == '0':
            config['backup']['compression'] = input("Enter the compression method (e.g., lz4, zstd, default is zstd): ")
            save_config(config)
        elif choice == '1':
            config['borg']['encryption'] = input("Enter the encryption type (e.g., repokey, none): ")
            save_config(config)
        elif choice == '2':
            config['borg']['repo'] = input("Enter the Borg repository path (e.g., user@backup-server:/path/to/repo): ")
            save_config(config)
        elif choice == '3':
            config['backup']['paths_to_backup'] = (input(f"Enter the directories to back up (comma-separated, default: /etc,/var,/home,/mnt,/root,/opt): ") or "/etc,/var,/home,/mnt,/root,/opt").split(',')
            config['backup']['exclude_patterns'] = (input(f"Enter exclude patterns (comma-separated, default: home/*/.cache/*,var/tmp/*): ") or "home/*/.cache/*,var/tmp/*").split(',')
            save_config(config)
        elif choice == '5':
            prune_settings = input("Enter prune settings (comma-separated in format d,w,m,y. Default is 30,0,0,0): ").split(',')
            config['backup']['prune'] = {
                'daily': prune_settings[0],
                'weekly': prune_settings[1],
                'monthly': prune_settings[2],
                'yearly': prune_settings[3]
            }
            save_config(config)
        elif choice == '6':
            os.system(f"nano {CONFIG_PATH}")  # Open the YAML file with nano for manual editing
        elif choice == '7':
            break  # Return to the main menu
        elif choice == 'E':
            exit_program()
        else:
            print("Invalid option. Please try again.")
