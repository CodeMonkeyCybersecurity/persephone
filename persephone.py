#Imports
import yaml
import os
import subprocess
import logging
from datetime import datetime
import socket  # Used to get the hostname

# Fle configuration path for backup configs
CONFIG_PATH = "/etc/CodeMonkeyCyber/Persephone/borgConfig.yaml"

# Set up logging to output to both a file and the console
file_handler = logging.FileHandler("/var/log/persephone.log")
file_handler.setLevel(logging.DEBUG)  # Log all levels to the log file

console_handler = logging.StreamHandler()
console_handler.setLevel(logging.ERROR)  # Only log errors or higher to the console

logging.basicConfig(
    level=logging.DEBUG,  # Overall log level
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[file_handler, console_handler]
)

# Error handling function 
def error_handler(func):
    """
    A decorator to handle errors for a given function. 
    It logs the error and provides consistent error handling.
    """
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except FileNotFoundError as fnf_error:
            logging.error(f"File not found: {fnf_error}")
            print(f"Error: {fnf_error}")
        except subprocess.CalledProcessError as cpe_error:
            logging.error(f"Command failed: {cpe_error.stderr}")
            print(f"Command error: {cpe_error.stderr}")
        except Exception as e:
            logging.error(f"An unexpected error occurred: {e}")
            print(f"An error occurred: {e}")
    return wrapper

# Main menu for selecting commands
@error_handler
def display_menu():
    """Display the main menu."""
    print("\nWelcome to Code Monkey Cybersecurity's backup tool, Persephone.py")
    print("We're so glad you're taking the time to back up your things")
    print("To learn more about us, visit cybermonkey.net.au")
    print("Please select an option:")
    print("(M) Show main (M)enu")
    print("(H) Need to ask for (H)elp? Good on you")
    print("(N) Run backup (N)ow")
    print("(E) (E)xit")
    print("(A) Automate backup     (Add backup config to crontab)")
    print("\nAvailable Borg Commands:")
    print("(1) benchmark           (Benchmark command)")
    print("(2) break-lock          (Break repository and cache locks)")
    print("(3) check               (Verify repository)")
    print("(4) compact             (Compact segment files / free space in repo)")
    print("(5) config              (Get and set configuration values)")
    print("(6) create              (Create backup)")
    print("(7) debug               (Debugging command)")
    print("(8) delete              (Delete archive)")
    print("(9) diff                (Find differences in archive contents)")
    print("(10) export-tar         (Create tarball from archive)")
    print("(11) extract            (Extract archive contents)")
    print("(12) info               (Show repository or archive information)")
    print("(13) init               (Initialize empty repository)")
    print("(14) key                (Manage repository key)")
    print("(15) list               (List archive or repository contents)")
    print("(16) mount              (Mount repository)")
    print("(17) prune              (Prune archives)")
    print("(18) recreate           (Re-create archives)")
    print("(19) rename             (Rename archive)")
    print("(20) serve              (Start repository server process)")
    print("(21) umount             (Umount repository)")
    print("(22) upgrade            (Upgrade repository format)")
    print("(23) with-lock          (Run user command with lock held)")
    print("(24) import-tar         (Create a backup archive from a tarball)")

# Mapping for Borg command functions
@error_handler
def handle_borg_command(choice):
    """Run the appropriate Borg command based on user input."""
    command_map = {
        '1': ['borg', 'benchmark'],
        '2': ['borg', 'break-lock'],
        '3': ['borg', 'check'],
        '4': ['borg', 'compact'],
        '5': ['borg', 'config'],
        '6': ['borg', 'create'],  # Add more arguments as necessary
        '7': ['borg', 'debug'],
        '8': ['borg', 'delete'],
        '9': ['borg', 'diff'],
        '10': ['borg', 'export-tar'],
        '11': ['borg', 'extract'],
        '12': ['borg', 'info'],
        '13': ['borg', 'init'],
        '14': ['borg', 'key'],
        '15': ['borg', 'list'],
        '16': ['borg', 'mount'],
        '17': ['borg', 'prune'],
        '18': ['borg', 'recreate'],
        '19': ['borg', 'rename'],
        '20': ['borg', 'serve'],
        '21': ['borg', 'umount'],
        '22': ['borg', 'upgrade'],
        '23': ['borg', 'with-lock'],
        '24': ['borg', 'import-tar']
    }
    
    if choice in command_map:
        run_borg_command(command_map[choice])
    else:
        print("Invalid command choice.")

# print("(H) Show (H)elp")
@error_handler
def show_borg_help():
    print("Asking for help? Good on you")
    """Displaying Borg's built-in help."""
    try:
        # Call the Borg help command
        subprocess.run(['borg', '--help'], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to display Borg help: {e.stderr}")
        print(f"Error displaying Borg help: {e.stderr}")
    finally:
        input("\nPress Enter to return to the submenu...")

        # Return to the submenu handler after displaying help
        submenu_handler()

# print("(N) Run backup (N)ow")
@error_handler
def run_borg_backup(config, dryrun=False):
    """Run the Borg backup using the configuration values."""
    try:
        # Start status update
        print("Starting Borg backup...")
        logging.info("Starting Borg backup.")

        # Extract relevant config details
        repo = config['borg']['repo']
        passphrase = config['borg']['passphrase']
        paths = config['backup']['paths_to_backup']
        compression = config['backup'].get('compression', 'zstd')  # Default to 'zstd' if not specified

        # Set up the environment for the passphrase
        env = os.environ.copy()
        env['BORG_PASSPHRASE'] = passphrase

        # Generate an archive name using the hostname and timestamp
        hostname = socket.gethostname()  # Get the actual hostname of the machine
        timestamp = datetime.now().strftime("%Y-%m-%dT%H:%M:%S")
        archive_name = f"{repo}::{hostname}-{timestamp}"

        # Build the Borg create command
        borg_create_cmd = ['borg', 'create', archive_name] + paths + [
            '--verbose',
            '--compression', compression,
            '--list',
            '--stats',
            '--show-rc',
            '--exclude-caches'
        ]

        # Add exclude patterns from config
        for pattern in config['backup'].get('exclude_patterns', []):
            borg_create_cmd += ['--exclude', pattern]

        # Add dry-run flag if specified
        if dryrun:
            borg_create_cmd.append('--dry-run')

        # Status update before running the command
        print("Running Borg backup command...")
        logging.info("Running Borg backup command.")
        
        # Run the Borg create command
        result = subprocess.run(borg_create_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)
        
        # Success update
        logging.info(result.stdout)  # Log the output of the command
        print(f"Borg backup completed successfully!\n{result.stdout}")  # Print the result to console

    except subprocess.CalledProcessError as e:
        # Failure update
        logging.error(f"Borg backup failed: {e.stderr}")
        print(f"Error: Borg backup failed. {e.stderr}")
        prompt_for_repository_menu()  # Prompt for repository fix if backup fails
        submenu_handler()

# print("(E) (E)xit")
@error_handler
def exit_program():
    """Exit the script."""
    print("Exiting the program. Goodbye!")
    exit()

# print("(A) Automate backup")   (Add backup config to crontab)
@error_handler
def add_borg_to_crontab(config):
    """Add Borg backup to crontab with error handling."""
    try:
        # Prompt user for the backup schedule
        print("Enter the time for the Borg backup (24-hour format):")
        
        # Input validation for minute
        while True:
            minute = input("Minute (0-59): ")
            if minute.isdigit() and 0 <= int(minute) <= 59:
                break
            print("Invalid input. Please enter a number between 0 and 59.")
        
        # Input validation for hour
        while True:
            hour = input("Hour (0-23): ")
            if hour.isdigit() and 0 <= int(hour) <= 23:
                break
            print("Invalid input. Please enter a number between 0 and 23.")
        
        # Input validation for day of month
        while True:
            day_of_month = input("Day of month (1-31, * for every day): ")
            if day_of_month.isdigit() and 1 <= int(day_of_month) <= 31 or day_of_month == "*":
                break
            print("Invalid input. Please enter a number between 1 and 31 or * for every day.")
        
        # Input validation for month
        while True:
            month = input("Month (1-12, * for every month): ")
            if month.isdigit() and 1 <= int(month) <= 12 or month == "*":
                break
            print("Invalid input. Please enter a number between 1 and 12 or * for every month.")
        
        # Input validation for day of the week
        while True:
            day_of_week = input("Day of week (0-6, Sunday is 0 or 7, * for every day): ")
            if day_of_week.isdigit() and 0 <= int(day_of_week) <= 7 or day_of_week == "*":
                break
            print("Invalid input. Please enter a number between 0 and 7 or * for every day.")

        # Ensure that user has entered values correctly
        cron_time = f"{minute} {hour} {day_of_month} {month} {day_of_week}"

        # Command to run Borg backup using the current configuration
        borg_backup_command = (
            f"borg create {config['borg']['repo']}::{socket.gethostname()}-{datetime.now().strftime('%Y-%m-%dT%H:%M:%S')} "
            f"{' '.join(config['backup']['paths_to_backup'])} "
            f"--compression {config['backup'].get('compression', 'zstd')} "
            f"--exclude-caches"
        )

        # Construct the crontab entry with logging
        cron_entry = f"{cron_time} {borg_backup_command} >> /var/log/eos_borg_backup.log 2>&1"

        # Check if the crontab entry already exists
        try:
            result = subprocess.run(['crontab', '-l'], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                current_crontab = result.stdout
            else:
                print("No crontab for this user. Starting fresh.")
                current_crontab = ""
        except subprocess.CalledProcessError as e:
            print(f"Error: Could not retrieve current crontab. {e.stderr}")
            logging.error(f"Error retrieving current crontab: {e.stderr}")
            return

        # Append the new cron entry if not already present
        if cron_entry not in current_crontab:
            new_crontab = current_crontab + f"\n{cron_entry}\n"
            try:
                # Update the crontab
                process = subprocess.run(['crontab', '-'], input=new_crontab, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                if process.returncode == 0:
                    print("Borg backup schedule added to crontab successfully.")
                    logging.info(f"Borg backup schedule added to crontab: {cron_entry}")
                else:
                    print(f"Error: Failed to update crontab. {process.stderr}")
                    logging.error(f"Error updating crontab: {process.stderr}")
            except subprocess.CalledProcessError as e:
                print(f"Error: Could not update crontab. {e.stderr}")
                logging.error(f"Failed to update crontab: {e.stderr}")
        else:
            print("This backup configuration already exists in crontab.")
            logging.info("Crontab entry already exists.")
    
    except Exception as e:
        print(f"An error occurred: {e}")
        logging.error(f"Error adding to crontab: {e}")
        submenu_handler()

# print("(1) benchmark           (Benchmark command)")
@error_handler
def benchmark_submenu():
    """Submenu for selecting the borg benchmark options and subcommands."""
    options = {
        '1': {'label': 'CRUD (Create, Read, Update, Delete)', 'action': lambda: run_borg_command(['borg', 'benchmark', 'crud'])},
        # Additional benchmark subcommands can go here if needed.
    }

    # Display the submenu using the existing submenu handler
    submenu_handler(options)

# print("(2) break-lock          (Break repository and cache locks)")
@error_handler

# print("(3) check               (Verify repository)")
@error_handler
def check_repo(config):
    """Check repository health with 'borg check'."""
    repo = config['borg']['repo']
    passphrase = config['borg']['passphrase']
    env = os.environ.copy()
    env['BORG_PASSPHRASE'] = passphrase

    try:
        result = subprocess.run(['borg', 'check', repo], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)
        logging.info(result.stdout)
        print(f"Repository check passed for {repo}.")  # Success message
        return True  # Indicate success
    except subprocess.CalledProcessError as e:
        logging.error(f"Repository check failed: {e.stderr}")
        print(f"Error: Repository check failed for {repo}. {e.stderr}")  # Failure message
        return False  # Indicate failure

# print("(4) compact             (Compact segment files / free space in repo)")
@error_handler
def borg_compact():
    """TBC"""
    try:
        # Call the Borg help command
        subprocess.run(['borg', '--help'], check=True)
    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to display Borg help: {e.stderr}")
        print(f"Error displaying Borg help: {e.stderr}")
    finally:
        input("\nPress Enter to return to the submenu...")

        # Return to the submenu handler after displaying help
        submenu_handler()
        
# print("(5) config              (Get and set configuration values)")
# Required configuration keys and their subkeys
REQUIRED_KEYS = {
    'borg': ['repo', 'passphrase', 'encryption', 'rsh'],
    'backup': ['paths_to_backup', 'exclude_patterns', 'compression', 'prune']
}

def validate_yaml_config():
    """Validate the YAML configuration file to ensure all required values are present."""
    if not os.path.exists(CONFIG_PATH):
        logging.error("Configuration file does not exist at the specified path.")
        print(f"Error: Configuration file not found at {CONFIG_PATH}. Please create it first.")
        return False
    
    try:
        # Load the YAML file
        with open(CONFIG_PATH, 'r') as file:
            config = yaml.safe_load(file)

        # Check for required keys and subkeys
        missing_keys = []
        for section, keys in REQUIRED_KEYS.items():
            if section not in config:
                missing_keys.append(section)
            else:
                for key in keys:
                    if key not in config[section]:
                        missing_keys.append(f"{section}.{key}")

        # If there are missing keys, log and print the details
        if missing_keys:
            logging.error(f"Missing configuration values: {', '.join(missing_keys)}")
            print(f"Error: The configuration is missing the following required values:\n - " +
                  "\n - ".join(missing_keys))
            return False

        # All keys are accounted for
        logging.info("Configuration file validated successfully, all values are accounted for.")
        print("Configuration file is complete and validated.")
        return True

    except yaml.YAMLError as e:
        logging.error(f"Error loading configuration file: {e}")
        print(f"Error: Could not load configuration file due to a YAML error. {e}")
        return False

@error_handler
def create_yaml_config():
    """Create the YAML config file at {CONFIG_PATH} with default values.

    This function allows the user to enter configuration settings for BorgBackup. If
    the user does not provide an input, the default value is used.
    """
    # Hardcoded default values
    hardcoded_defaults = {
        'borg': {
            'repo': "user@backup-hostname:/path/to/borgRepo",
            'passphrase': "SecretPassword",
            'encryption': "repokey",
            'rsh': "ssh -i /path/to/id_ed25519" 
        },
        'backup': {
            'paths_to_backup': ["/var", "/etc", "/home", "/root", "/opt", "/mnt", "/usr"],
            'exclude_patterns': ["home/*/.cache/*", "var/tmp/*"],
            'compression': "zstd"
        }
    }
    
    # Load existing config if it exists, else use hardcoded defaults
    config = load_config() or hardcoded_defaults

    # Prompt user for each setting, using the loaded value as the default
    config['borg']['repo'] = input(f"Enter the Borg repository path (default: {config['borg']['repo']}): ") or config['borg']['repo']
    config['borg']['passphrase'] = input(f"Enter the Borg passphrase (default: {config['borg']['passphrase']}): ") or config['borg']['passphrase']
    config['borg']['encryption'] = input(f"Enter the encryption type (e.g., repokey, none, default: {config['borg']['encryption']}): ") or config['borg']['encryption']

    # Prompt user for the SSH command if they want to set it
    config['borg']['rsh'] = input(f"Enter the SSH command for Borg (default: {config['borg']['rsh']}): ") or config['borg']['rsh']
    
    # Get backup settings
    paths_to_backup = input(f"Enter the directories to back up (comma-separated, default: {','.join(config['backup']['paths_to_backup'])}): ")
    config['backup']['paths_to_backup'] = paths_to_backup.split(',') if paths_to_backup else config['backup']['paths_to_backup']

    #Exclude patterns
    exclude_patterns = input(f"Enter exclude patterns (comma-separated, default: {','.join(config['backup']['exclude_patterns'])}): ")
    config['backup']['exclude_patterns'] = exclude_patterns.split(',') if exclude_patterns else config['backup']['exclude_patterns']

    # Compression
    config['backup']['compression'] = input(f"Enter the compression method (e.g., lz4, zstd, default: {config['backup']['compression']}): ") or config['backup']['compression']

    # Get prune settings
    config['backup']['prune']['daily'] = int(input(f"Enter the number of daily archives to keep (default: {config['backup']['prune']['daily']}): ") or config['backup']['prune']['daily'])
    config['backup']['prune']['weekly'] = int(input(f"Enter the number of weekly archives to keep (default: {config['backup']['prune']['weekly']}): ") or config['backup']['prune']['weekly'])
    config['backup']['prune']['monthly'] = int(input(f"Enter the number of monthly archives to keep (default: {config['backup']['prune']['monthly']}): ") or config['backup']['prune']['monthly'])
    config['backup']['prune']['yearly'] = int(input(f"Enter the number of yearly archives to keep (default: {config['backup']['prune']['yearly']}): ") or config['backup']['prune']['yearly'])

    # Save the configuration to YAML
    save_config(config)
    print(f"Configuration file updated successfully at {CONFIG_PATH}")

def load_config():
    """Load configuration from YAML file."""
    if os.path.exists(CONFIG_PATH):
        try:
            with open(CONFIG_PATH, 'r') as file:
                config = yaml.safe_load(file)
                logging.info("Configuration loaded successfully.")
                return config
        except yaml.YAMLError as e:
            logging.error(f"Error loading configuration file: {e}")
            return None
    else:
        logging.error(f"Configuration file not found.")
        return None

def save_config(config):
    """Save the modified YAML config file."""
    try:
        with open(CONFIG_PATH, 'w') as file:
            yaml.safe_dump(config, file)
        logging.info(f"Configuration updated and saved to {CONFIG_PATH}.")
    except OSError as e:
        logging.error(f"Failed to write the configuration file: {e}")

# print("(6) create              (Create backup)")
@error_handler
def create_borg_repository(config):
    """Create a new Borg backup based on the configuration values."""
    while not validate_yaml_config():
        retry = input("Configuration is incomplete or invalid. Would you like to go back to configure it? (Y/N): ").strip().lower()
        if retry == 'y':
            create_yaml_config()  # Call the configuration setup
            config = load_config()  # Reload the updated config
        else:
            print("Exiting. Please update the configuration file and try again.")
            return False  # Exit if user chooses not to retry
            
    try:
        # Retrieve Borg configurations
        repo = config['borg'].get('repo')
        passphrase = config['borg'].get('passphrase')
        encryption_type = config['borg'].get('encryption', 'repokey')  # Default to 'repokey' if not set
        rsh = config['borg'].get('rsh')  # Optional SSH command for Borg RSH

        # Set up environment for Borg with passphrase and RSH if provided
        env = os.environ.copy()
        env['BORG_PASSPHRASE'] = passphrase
        if rsh:
            env['BORG_RSH'] = rsh  # Set the custom RSH command if specified

        # Check disk space in temporary directory
        tmp_dir = "/tmp"
        if os.path.exists(tmp_dir):
            result = subprocess.run(['df', '-h', tmp_dir], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            if result.returncode == 0:
                output = result.stdout
                logging.info(f"Disk space check for {tmp_dir}:\n{output}")
                print(f"Disk space check for {tmp_dir}:\n{output}")
                env["TMPDIR"] = tmp_dir  # Set TMPDIR in the environment
            else:
                logging.error(f"Error checking disk space: {result.stderr}")
                print(f"Error: Disk space check failed. {result.stderr}")
        else:
            raise FileNotFoundError(f"Temporary directory {tmp_dir} does not exist")

        # Check SSH key for Borg RSH if required
        ssh_key_path = os.path.expanduser("~/.ssh/id_ed25519")
        if os.path.exists(ssh_key_path):
            env["BORG_RSH"] = f"ssh -i {ssh_key_path}"
            logging.info(f"BORG_RSH set to use SSH key: {ssh_key_path}")
        else:
            logging.warning(f"SSH key not found at {ssh_key_path}. RSH will be used as configured.")

        # Run Borg init command to create the repository
        borg_init_cmd = ['borg', 'init', '--encryption', encryption_type, repo]
        result = subprocess.run(borg_init_cmd, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, env=env, text=True)

        logging.info(f"Repository {repo} created successfully.")
        print(f"Repository {repo} created successfully.")  # Success message
        return True  # Indicate success

    except subprocess.CalledProcessError as e:
        logging.error(f"Failed to create Borg repository: {e.stderr}")
        print(f"Error: Failed to create repository {repo}. {e.stderr}")  # Failure message
        return False  # Indicate failure
    except Exception as e:
        logging.error(f"An error occurred during repository creation: {e}")
        print(f"Error: {e}")
        return False


# print("(7) debug               (Debugging command)")
@error_handler

# print("(8) delete              (Delete archive)")
@error_handler

# print("(9) diff                (Find differences in archive contents)")
@error_handler

# print("(10) export-tar         (Create tarball from archive)")
@error_handler

# print("(11) extract            (Extract archive contents)")
@error_handler

# print("(12) info               (Show repository or archive information)")
@error_handler

# print("(13) init               (Initialize empty repository)")
@error_handler

# print("(14) key                (Manage repository key)")
@error_handler

# print("(15) list               (List archive or repository contents)")
@error_handler

# print("(16) mount              (Mount repository)")
@error_handler

# print("(17) prune              (Prune archives)")
@error_handler

# print("(18) recreate           (Re-create archives)")
@error_handler

# print("(19) rename             (Rename archive)")
@error_handler

# print("(20) serve              (Start repository server process)")
@error_handler


# print("(21) umount             (Umount repository)")
@error_handler
# print("(22) upgrade            (Upgrade repository format)")
@error_handler

# print("(23) with-lock          (Run user command with lock held)")
@error_handler

# print("(24) import-tar         (Create a backup archive from a tarball)")
@error_handler

# OTHER FUNCTIONS

# Modify the repository_options_menu function to show success/failure
@error_handler

# Handle submenu option
@error_handler
def submenu_handler(options):
    """
    Displays the submenu options and handles user input.
    :param options: A dictionary where keys are option numbers and values are the command or function to run.
    """
    while True:
        # Display submenu options
        print("\nSubmenu Options:")
        for key, value in options.items():
            print(f"({key}) {value['label']}")

        # Add common options for all submenus
        print("(M) Return to main menu")
        print("(E) Exit")

        # Get user choice
        choice = input("Select an option: ").upper()

        if choice == 'M':
            display_menu()
            break  # Exit submenu and return to the main menu
        elif choice == 'E':
            exit_program()
        elif choice in options:
            # Call the associated function or command for the choice
            options[choice]['action']()
        else:
            print("Invalid option. Please try again.")

# Helper function to run Borg commands
@error_handler
def run_borg_command(command):
    """Run a specific Borg command."""
    try:
        result = subprocess.run(command, check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        logging.info(result.stdout)
        print(f"Command executed successfully:\n{result.stdout}")
    except subprocess.CalledProcessError as e:
        logging.error(f"Command failed: {e.stderr}")
        print(f"Error: {e.stderr}")

# Clear the screen
@error_handler
def clear_screen():
    """Clear the terminal screen."""
    os.system('clear')

# Main program loop with command mapping
@error_handler
def main():
    try:
        while True:
            clear_screen()
            display_menu()
            choice = input("Select an option or Borg command number: ").upper()
            
            command_map = {
                'M': display_menu,
                'H': show_borg_help,
                'N': run_borg_backup,
                'A': add_borg_to_crontab,
                'E': exit_program,
                '1': benchmark_command,      # Example function to run the benchmark
                '2': break_lock_command,     # Example function to break repository locks
                '3': check_repository,       # Verify repository
                '4': compact_repository,     # Compact segment files
                '5': create_yaml_config,     # Config setup
                '6': create_borg_backup,     # Create backup
                '7': debug_command,          # Debugging
                '8': delete_archive,         # Delete archive
                '9': diff_archives,          # Find differences
                '10': export_tar,            # Export tarball
                '11': extract_archive,       # Extract archive
                '12': show_info,             # Show repository info
                '13': init_repository,       # Initialize repository
                '14': manage_key,            # Manage repository key
                '15': list_contents,         # List repository contents
                '16': mount_repository,      # Mount repository
                '17': prune_archives,        # Prune archives
                '18': recreate_archives,     # Re-create archives
                '19': rename_archive,        # Rename archive
                '20': serve_repository,      # Start server process
                '21': unmount_repository,    # Umount repository
                '22': upgrade_format,        # Upgrade format
                '23': with_lock,             # Run command with lock held
                '24': import_tar,            # Import tar to archive
            }
    
            if choice in command_map:
                command_map[choice]()  # Call the function mapped to the choice
            else:
                print("Invalid option. Please try again.")

    except KeyboardInterrupt:
        print("\nProgram interrupted. Exiting gracefully.")
        exit()

if __name__ == "__main__":
    main()
