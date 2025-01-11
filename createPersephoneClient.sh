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
echo "${RESTIC_PASS}" | sudo tee /root/.restic-password >/dev/null
sudo chmod 600 /root/.restic-password

# Define the repository URL
# Adjust 'henry@backup' and path to match your actual backup server + path
RESTIC_REPO="sftp:$PERS_SRV_USER@$PERS_SRV_HOSTNAME:/$SRV_DIR/$(hostname)"

echo "${RESTIC_REPO}" | sudo tee /root/.restic-repo >/dev/null
sudo chmod 600 /root/.restic-repo

echo "Restic repository configuration files created:"
echo "  - /root/.restic-password"
echo "  - /root/.restic-repo"
echo "Done."