import subprocess

def addBorgToCrontab(config):
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
