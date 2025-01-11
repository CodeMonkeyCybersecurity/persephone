import subprocess

def checkCrontab():
    """
    Function to check crontab entries for the current user.
    Logs the entries to the specified log file and prints them to the console.
    """
    try:
        # Execute the crontab -l command
        result = subprocess.run(['crontab', '-l'], text=True, capture_output=True, check=True)

        # Log and print the output
        logging.info("Current crontab entries for the user:")
        print("Current crontab entries for the user:")
        for line in result.stdout.splitlines():
            logging.info(line)
            print(line)
    except subprocess.CalledProcessError as e:
        # Handle cases where the crontab is empty or there is an error
        logging.error("Failed to retrieve crontab entries. Error: %s", e)
        print("No crontab entries found or an error occurred.")
