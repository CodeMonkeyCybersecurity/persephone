import shutil
import sys

if shutil.which("borg") is None:
    print("Error: Borg Backup is not installed. Please install it to proceed.")
    sys.exit(1)
