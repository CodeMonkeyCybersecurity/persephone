#!/usr/bin/env bash
#
# createPersephoneClient.sh

set -euo pipefail

# -----------------------------
# Main Script
# -----------------------------

# Prompt for Restic repository password
read -rp "Enter your repository password: " RESTIC_PASS

echo "Storing Restic password in /root/.restic-password..."
echo "${RESTIC_PASS}" | sudo tee /root/.restic-password
sudo chmod 600 /root/.restic-password

# Define the repository URL
# Adjust 'henry@backup' and path to match your actual backup server + path
read -p "What is the location of your persephone repository? (eg. user@backup-host:/path/to/persephone/repo): " PERS_REPO

echo "Initializing Restic repository at ${PERS_REPO}/$(hostname)..."

sudo restic -r "${PERS_REPO}/$(hostname)" init

echo "Restic repository initialized at ${PERS_REPO}/$(hostname)."

echo "${PERS_REPO}" | sudo tee /root/.restic-repo 
sudo chmod 600 /root/.restic-repo

echo "Restic repository configuration files created:"
echo "  - /root/.restic-password"
echo "  - /root/.restic-repo"
echo "Done."