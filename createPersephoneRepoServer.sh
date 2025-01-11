#!/usr/bin/env bash
#
# createPersephoneRepoServer.sh

set -euo pipefail

# -----------------------------
# Directories
# -----------------------------
SRV_DIR='/srv/codeMonkeyCyber'  # Directory where Restic repos will live
LOG_DIR='/var/log/codeMonkeyCyber'

# -----------------------------
# Main Script
# -----------------------------
echo "Setting up backup repository on server..."

# 1. Create server directory for backups
sudo mkdir -p "${SRV_DIR}"

# 2. Secure ownership & permissions (assuming root ownership)
sudo chown -R root:root "${SRV_DIR}"
# 700 ensures only root can access it
sudo chmod 600 "${SRV_DIR}"

echo "Server repository directory set up at ${SRV_DIR} with restricted permissions."
PERS_SRV_USER=$(whoami)
PERS_SRV_HOSTNAME=$(hostname)
echo "This server is located at $PERS_SRV_USER@$PERS_SRV_HOSTNAME:/$SRV_DIR"
echo "It is important you note this down somewhere"

# (Optional) Initialize a default Restic repo. You can comment this out
# if you prefer to initialize from the client side or with separate script.
# echo "Initializing Restic repository..."
# sudo restic -r "${SRV_DIR}/$(hostname)" init
# echo "Restic repository initialized at ${SRV_DIR}/$(hostname)."