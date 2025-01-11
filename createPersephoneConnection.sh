#!/usr/bin/env bash
#
# createPersephoneConnection.sh

set -euo pipefail

# -----------------------------
# Main Script
# -----------------------------
echo "Generating SSH key for passwordless backup..."

# Generate the SSH key (adjust parameters as needed)
sudo ssh-keygen -t rsa -b 4096 -N '' -f /root/.ssh/id_rsa

# Copy the SSH key to the backup server (adjust username@host accordingly)
sudo ssh-copy-id henry@backup

echo "SSH key copied. You should now be able to SSH into henry@backup without a password."