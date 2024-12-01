#!/bin/bash

# Function to test restore
test_restore() {
    check_borg_installed
    if [ -z "$BORG_REPO" ]; then
        error_exit "BORG_REPO is not set. Exiting."
    fi
    read -p "Enter the archive name to restore: " archive_name
    read -p "Enter the destination directory: " dest_dir
    echo "Restoring archive $archive_name to $dest_dir" | tee -a $LOGFILE
    borg extract "$BORG_REPO::$archive_name" "$dest_dir" | tee -a $LOGFILE
    echo "Restore operation completed." | tee -a $LOGFILE
}
