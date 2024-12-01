# Set up log file
LOGFILE=~/borgbackup/check_borg.log
echo "BorgBackup Check Log - $(date)" > $LOGFILE

# Function to log and handle errors
error_exit() {
    echo "$1" | tee -a $LOGFILE 1>&2
    exit 1
}
