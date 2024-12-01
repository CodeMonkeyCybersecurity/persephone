# Function to check BorgBackup logs
check_logs() {
    if [ -f ~/borgbackup/backup.log ]; then
        echo "Displaying BorgBackup logs:" | tee -a $LOGFILE
        cat ~/borgbackup/backup.log | tee -a $LOGFILE
    else
        echo "Log file not found." | tee -a $LOGFILE
    fi
}
