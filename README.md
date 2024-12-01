## Only the scripts in the main directory are tested and confirmed to be good to use. Use the rest at your own risk; these are in the various stages of drafting and development.

A universal backup and recovery solution... actually just the mighty borg backup all dressed up

# Persephone: Enhanced Borg Backup Wrapper

**Persephone** is a Python-based solution designed to simplify and enhance the use of Borg for backups and recovery, providing additional features like centralized management, automated scheduling, and modular configuration.

## Getting Started

## Prerequisites

- **Borg Backup**: Ensure Borg Backup is installed on your system. Installation instructions can be found on the [official Borg website](https://www.borgbackup.org/).
- You can check whether Borg Backup is installed by running
   ```
   borg --version
   ```
   
### Installation
1. Clone the repository:
   ```
   git clone https://github.com/CodeMonkeyCybersecurity/Persephone.git

2.	Navigate to the Project Directory:
   ```
   cd Persephone
   ```

3. Install the dependencies:
   ```
   pip install -r requirements.txt
   ```

4. Create your configuration file, config.yaml, to define your backup targets, encryption type, and repository paths by running
   ```
   python3 getStarted.py
   ```


### Calling the error logger in a main script
```
from error_logger import ErrorLogger

# Initialize the logger
logger = ErrorLogger("app_errors.log")

try:
    # Code that may raise an exception
    1 / 0
except Exception as e:
    # Log the error with a custom message
    logger.log_error("Division by zero error occurred.")
```


## Complaints, compliments, confusion and other communications:

Secure email: [git@cybermonkey.net.au](mailto:git@cybermonkey.net.au)  

Website: [cybermonkey.net.au](https://cybermonkey.net.au)

```
     ___         _       __  __          _
    / __|___  __| |___  |  \/  |___ _ _ | |_____ _  _
   | (__/ _ \/ _` / -_) | |\/| / _ \ ' \| / / -_) || |
    \___\___/\__,_\___| |_|  |_\___/_||_|_\_\___|\_, |
                  / __|  _| |__  ___ _ _         |__/
                 | (_| || | '_ \/ -_) '_|
                  \___\_, |_.__/\___|_|
                      |__/
```
