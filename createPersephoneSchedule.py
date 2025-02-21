#!/usr/bin/env python3
"""
createPersephoneSchedule.py

- Checks the current crontab for any lines containing "restic" (ignoring comments).
- Backs up the current crontab.
- If restic lines are found, asks the user if they want them deleted.
  - If yes, those lines are removed.
  - If no, prints a warning that multiple restic lines may lead to undesired outcomes.
- Prompts the user for a new cron schedule (5 fields: minute hour day-of-month month day-of-week).
- Asks if the minute should be randomized.
- Appends a new cron job line to run /opt/persephone/persephone.sh with the chosen schedule.
- Updates the crontab and prints the changed crontab.
"""

import subprocess
import os
import datetime
import random

def load_crontab():
    """Returns the current crontab as a list of lines."""
    try:
        result = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=True)
        return result.stdout.splitlines()
    except subprocess.CalledProcessError:
        # No crontab exists
        return []

def backup_crontab(lines):
    """Backs up the current crontab to a file with a timestamp."""
    timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    backup_filename = f"crontab_backup_{timestamp}.txt"
    with open(backup_filename, "w") as f:
        f.write("\n".join(lines) + "\n")
    print(f"Crontab backed up to {backup_filename}")

def remove_restic_lines(lines):
    """Returns a new list of lines with any non-comment lines containing 'restic' removed."""
    new_lines = []
    removed_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith("#") and "restic" in stripped:
            removed_lines.append(line)
        else:
            new_lines.append(line)
    return new_lines, removed_lines

def prompt_input(prompt_message, default_val=None):
    if default_val:
        prompt = f"{prompt_message} [{default_val}]: "
    else:
        prompt = f"{prompt_message}: "
    resp = input(prompt).strip()
    return resp if resp else default_val

def get_cron_schedule():
    """Prompts the user for a cron schedule (5 fields) and returns them as a list."""
    while True:
        schedule = prompt_input("Enter cron schedule (minute hour day-of-month month day-of-week)", "* * * * *")
        fields = schedule.split()
        if len(fields) == 5:
            return fields
        else:
            print("Invalid schedule. Please enter exactly 5 space-separated fields (e.g., '* 2 * * *').")

def main():
    # Load and back up current crontab.
    current_cron = load_crontab()
    backup_crontab(current_cron)
    
    # Check for lines containing "restic" (non-comment).
    new_cron, removed = remove_restic_lines(current_cron)
    if removed:
        print("\nFound the following restic-related lines in your crontab:")
        for line in removed:
            print("  " + line)
        choice = prompt_input("Do you want to delete these lines? (Y/n)", "Y")
        if choice.lower() not in ["y", "yes"]:
            print("WARNING: Multiple restic lines in the crontab may lead to undesired outcomes.")
        else:
            current_cron = new_cron  # Remove the restic lines

    # Get new cron schedule.
    cron_fields = get_cron_schedule()
    # Ask if the user wants to randomize the minute field.
    rand_choice = prompt_input("Randomize the minute field? (y/N)", "N")
    if rand_choice.lower() in ["y", "yes"]:
        random_minute = str(random.randint(0,59))
        cron_fields[0] = random_minute
        print(f"Minute field randomized to {random_minute}")
    new_schedule = " ".join(cron_fields)
    
    # Build the new cron line.
    # The backup command is assumed to be /opt/persephone/persephone.sh
    new_cron_line = f'{new_schedule} /opt/persephone/persephone.sh'
    print("\nNew cron line to be added:")
    print(new_cron_line)
    
    # Append the new cron line to the current crontab lines.
    current_cron.append(new_cron_line)
    new_cron_content = "\n".join(current_cron) + "\n"
    
    # Update the crontab.
    try:
        subprocess.run(["crontab", "-"], input=new_cron_content, text=True, check=True)
        print("\nCrontab updated successfully. New crontab:")
        updated = subprocess.run(["crontab", "-l"], capture_output=True, text=True, check=True)
        print(updated.stdout)
    except subprocess.CalledProcessError as e:
        print("Error updating crontab:", e)

if __name__ == "__main__":
    main()
