import subprocess
import sys

def check_borg_installed():
    try:
        subprocess.run(['borg', '--version'], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("Borg Backup is not installed. Please install it to proceed.")
        sys.exit(1)

# Call the function at the start of your script
check_borg_installed()
