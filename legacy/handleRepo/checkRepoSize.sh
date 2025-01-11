#!/bin/bash

# Function to check the repository size
monitor_size() {
    check_borg_installed
    if [ -z "$BORG_REPO" ]; then
        error_exit "BORG_REPO is not set. Exiting."
    fi
    echo "Calculating the size of the repository:" | tee -a $LOGFILE
    du -sh "$BORG_REPO" | tee -a $LOGFILE
}
