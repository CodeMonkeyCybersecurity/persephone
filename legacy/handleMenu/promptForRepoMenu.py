# Prompt user to go to repository menu
def promptForRepoMenu():
    """Prompt the user if they want to go to the repository options menu."""
    while True:
        user_input = input("The repository is invalid. Would you like to go to the repository options to fix it? (y/N): ").lower()
        if user_input == 'y':
            repository_options_menu()
            break
        elif user_input == 'n' or user_input == '':
            break
        else:
            print("Invalid input. Please type 'y' for Yes or 'n' for No.")
