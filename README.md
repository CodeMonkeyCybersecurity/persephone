# Persephone: Enhanced Restic Backup Wrapper

**Persephone** is a solution designed to simplify and enhance the use of Restic for backups and recovery, providing additional features like centralized management, automated scheduling, and modular configuration.

This will currently work only on debian-based systems (eg. Ubuntu, Debian, Kali). **Work is ongoing to expand this to MacOS and Windows.**

## Installation

### 1. Create the install directory:
```
OPT_DIR='/opt/codeMonkeyCyber'
PERS_USER=$(whoami)

# Ensure the directory exists first
sudo mkdir -p $OPT_DIR

# Change ownership of the directory
sudo chown -R $PERS_USER:$PERS_USER $OPT_DIR

# Set appropriate permissions (755 for directories, 644 for files)
sudo find $OPT_DIR -type d -exec chmod 755 {} \;  # Directories
sudo find $OPT_DIR -type f -exec chmod 644 {} \;  # Files

# Verify directory contents and ownership/permissions
ls -lah $OPT_DIR

# Change to the directory
cd $OPT_DIR

# Print the working directory
pwd  # Verify that the working directory has been updated
```

### 2. & 3. Clone the repository and navigate to the Project Directory
```
git clone https://github.com/CodeMonkeyCybersecurity/persephone.git
cd persephone
```
OR 
```
gh repo clone CodeMonkeyCybersecurity/persephone
cd persephone
```

### 4. Install the dependencies:
```
sudo ./installPersephone.sh
```

### 5. On the computer your backing up to
```
./createPersephoneServer.sh
```

### 6. On the computer your backing up from
```
./createPersephoneClient.sh
```

### 7. Create connections between the two computers, so they can talk to each other
```
./createPersephoneConnection.sh
```

### 8. Backup
```
./createPersephoneBackup.sh
```


## Relevant directories and files:
```
# Directories
OPT_DIR='/opt/codeMonkeyCyber'
SRV_DIR='/srv/codeMonkeyCyber'
INSTALL_DIR='/opt/codeMonkeyCyber/persephone'

# Configurations
CONFIG_FILE='/etc/codeMonkeyCyber/persephone/persephone.conf'

# Logging
LOG_DIR='/var/log/codeMonkeyCyber'
LOG_FILE=f'{LOG_DIR}/persephone.log'

# Scripts
SUBMODULES_DEST='/usr/local/bin/persephone'
```


## Complaints, compliments, confusion:

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
