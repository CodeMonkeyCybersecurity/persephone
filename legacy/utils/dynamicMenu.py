import os

# Error handling decorator (for consistency with other Persephone scripts)
def error_handler(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except Exception as e:
            print(f"Error in {func.__name__}: {e}")
            raise e
    return wrapper

# Function to display dynamically generated menu
@error_handler
def display_menu(directory="."):
    files = [f for f in os.listdir(directory) if os.path.isfile(f)]
    
    if not files:
        print("No files found in the current directory.")
        return

    print("\n=== Persephone File Selection Menu ===")
    for idx, file in enumerate(files, start=1):
        print(f"{idx}. {file}")

    print(f"{len(files) + 1}. Exit")

    # Get user selection with a default option to exit
    default_choice = len(files) + 1
    choice = input(f"Choose an option (default {default_choice}): ") or str(default_choice)

    try:
        choice = int(choice)
        if 1 <= choice <= len(files):
            selected_file = files[choice - 1]
            print(f"You selected: {selected_file}")
            # Perform actions with the selected file here
            return selected_file
        elif choice == len(files) + 1:
            print("Exiting.")
        else:
            print("Invalid choice. Exiting.")
    except ValueError:
        print("Invalid input. Exiting.")

# Main execution function
@error_handler
def main():
    print("Welcome to the Persephone Modular Menu System")
    selected_file = display_menu()

    if selected_file:
        # Placeholder for additional actions, if needed
        print(f"Processing {selected_file}...")
    else:
        print("No file selected.")

if __name__ == "__main__":
    main()
