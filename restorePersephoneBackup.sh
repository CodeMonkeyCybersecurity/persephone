#!/usr/bin/env bash
#
# restorePersephoneBackup.sh

set -euo pipefail

# -----------------------------
# Directories and Config
# -----------------------------

REPO_FILE="/root/.restic-repo"
PASS_FILE="/root/.restic-password"

# -----------------------------
# Functions
# -----------------------------

# Function to list snapshots and return them as an array
list_snapshots() {
    sudo restic \
        --repository-file "${REPO_FILE}" \
        --password-file "${PASS_FILE}" \
        snapshots --json | jq -r '.[] | "\(.short_id) \(.time) \(.paths[])"'
}

# Function to prompt user to select a snapshot
select_snapshot() {
    echo "Available Snapshots:"
    echo "-------------------"

    # Retrieve snapshots
    mapfile -t snapshots < <(list_snapshots)

    if [ ${#snapshots[@]} -eq 0 ]; then
        echo "No snapshots found."
        exit 1
    fi

    # Display snapshots with numbering
    for i in "${!snapshots[@]}"; do
        printf "%3d) %s\n" $((i + 1)) "${snapshots[i]}"
    done

    echo
    # Prompt user for selection
    while true; do
        read -rp "Enter the number of the snapshot you want to restore: " selection
        if [[ "$selection" =~ ^[0-9]+$ ]] && [ "$selection" -ge 1 ] && [ "$selection" -le "${#snapshots[@]}" ]; then
            selected_snapshot=$(echo "${snapshots[$((selection - 1))]}" | awk '{print $1}')
            echo "You have selected snapshot: ${selected_snapshot}"
            break
        else
            echo "Invalid selection. Please enter a number between 1 and ${#snapshots[@]}."
        fi
    done
}

# Function to perform restoration
restore_snapshot() {
    echo "Starting restoration process for snapshot ${selected_snapshot}..."
    
    # Prompt for confirmation
    read -rp "Are you sure you want to restore this snapshot? This may overwrite existing files. (y/N): " confirm
    case "$confirm" in
        [yY][eE][sS]|[yY]) 
            ;;
        *)
            echo "Restoration canceled."
            exit 0
            ;;
    esac

    # Perform the restore
    sudo restic \
        --repository-file "${REPO_FILE}" \
        --password-file "${PASS_FILE}" \
        restore "${selected_snapshot}" --target /

    echo "Restoration of snapshot ${selected_snapshot} completed successfully."
}

# -----------------------------
# Main Script
# -----------------------------

echo "Checking Restic backup and snapshots..."
echo

# Ensure jq is installed for JSON parsing
if ! command -v jq &> /dev/null; then
    echo "The 'jq' utility is required but not installed. Please install it and retry."
    exit 1
fi

select_snapshot
restore_snapshot

echo "Restic restore process complete."
