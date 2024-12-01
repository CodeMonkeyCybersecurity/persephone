# Function to set up notifications
setup_notifications() {
    read -p "Enter your email address for notifications: " email
    if [ -z "$email" ]; then
        error_exit "No email provided. Exiting."
    fi
    echo "Setting up notifications for backup failures..." | tee -a $LOGFILE
    # Add mail sending logic to the backup script
    echo "if [ \${global_exit} -ne 0 ]; then" >> ~/borgbackup/backup_script.sh
    echo "    echo 'BorgBackup failed on \$(hostname)' | mail -s 'BorgBackup Failure' $email" >> ~/borgbackup/backup_script.sh
    echo "fi" >> ~/borgbackup/backup_script.sh
    echo "Notification setup completed." | tee -a $LOGFILE
}
