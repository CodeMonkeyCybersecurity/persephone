# Handle submenu option
def handle_submenu_option(option):
    """Handle user options from the submenu."""
    config = load_config()

    if option == '0' and config:
        run_borg_backup(config)
    elif option == '1':
        print("Current configuration:")
        print(config)
    elif option == '2':
        create_yaml_config()
    elif option == '3' and config:
        edit_yaml_menu(config)  # Go to YAML edit menu
    elif option == '4' and config:
        run_borg_backup(config, dryrun=True)
    elif option == '5' and config:
        try:
            os.remove(CONFIG_PATH)
            print("Configuration deleted.")
        except OSError as e:
            print(f"Error deleting configuration: {e}")
    elif option == '6':
        create_yaml_config()
    elif option == 'M':
        return
    elif option == 'E':
        exit_program()
    else:
        print("Invalid option or no configuration available. Please choose a valid option.")
