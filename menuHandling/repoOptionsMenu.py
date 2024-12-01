# Modify the repository_options_menu function to show success/failure
def repoOptionsMenu():
    """Handle the repository options menu."""
    while True:
        print("\nRepository Options:")
        print("(1) View current repository path")
        print("(2) Change repository path")
        print("(3) Check repository health")
        print("(4) Create a new repository")  # Add option to create new repository
        print("(M) Return to main menu")
        print("(E) Exit")

        choice = input("Select an option: ").upper()

        if choice == '1':
            config = load_config()
            if config:
                print(f"Current repository: {config['borg']['repo']}")
        elif choice == '2':
            config = load_config()
            if config:
                config['borg']['repo'] = input("Enter the new repository path (e.g., user@backup-server:/path/to/repo): ")
                save_config(config)
                print("Repository path updated successfully.")  # Indicate success
        elif choice == '3':
            config = load_config()
            if config:
                success = check_repo(config)
                if success:
                    print("Repository health check completed successfully.")  # Indicate success
                else:
                    print("Repository health check failed.")  # Indicate failure
        elif choice == '4':  # Create a new repository
            config = load_config()
            if config:
                success = create_borg_repository(config)
                if success:
                    print("New repository created successfully.")  # Indicate success
                else:
                    print("Failed to create the repository.")  # Indicate failure
        elif choice == 'M':
            break
        elif choice == 'E':
            exit_program()
        else:
            print("Invalid option. Please try again.")
