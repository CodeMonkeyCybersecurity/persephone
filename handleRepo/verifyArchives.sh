#!/bin/bash

# Function to verify backup archives
verify_archives() {
    check_borg_installed
    if [ -z "$BORG_REPO" ]; then
        error_exit "BORG_REPO is not set. Exiting."
    fi
    echo "Listing archives in the repository:" | tee -a $LOGFILE
    borg list "$BORG_REPO" | tee -a $LOGFILE
}
