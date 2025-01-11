#!/bin/bash

# Function to run multiple checks
runAllChecks() {
    check_borg_installed
    check_logs
    verify_archives
    check_crontab
    review_configs
    monitor_size
}

# Function to prompt for checks
prompt_check_type() {
    echo "What would you like to check?"
    echo "1. Check BorgBackup logs"
    echo "2. Verify backup archives"
    echo "3. Test restore"
    echo "4. Check crontab entries"
    echo "5. Review borg_configs.md"
    echo "6. Check the repository size"
    echo "7. Set up notifications"
    echo "8. Run all checks"
    read -p "Please enter your choice (1 - 8): " choice

    case $choice in
        1)
            check_logs
            ;;
        2)
            verify_archives
            ;;
        3)
            test_restore
            ;;
        4)
            check_crontab
            ;;
        5)
            review_configs
            ;;
        6)
            monitor_size
            ;;
        7)
            setup_notifications
            ;;
        8)
            run_all_checks
            ;;
        *)
            error_exit "Invalid choice. Exiting."
            ;;
    esac
}

# Check if an argument was provided
if [ $# -eq 0 ]; then
    prompt_check_type
else
    case $1 in
        logs)
            check_logs
            ;;
        archives)
            verify_archives
            ;;
        restore)
            test_restore
            ;;
        crontab)
            check_crontab
            ;;
        configs)
            review_configs
            ;;
        size)
            monitor_size
            ;;
        notifications)
            setup_notifications
            ;;
        all)
            run_all_checks
            ;;
        *)
            error_exit "Invalid argument. Exiting."
            ;;
    esac
fi
