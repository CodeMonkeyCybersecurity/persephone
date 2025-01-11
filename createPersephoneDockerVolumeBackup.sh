#!/usr/bin/env bash
#
# createPersephoneDockerBackup.sh
#
# This script stops Docker entirely, backs up your system 
# (including Docker volumes), then restarts Docker.

set -euo pipefail

# Restic repository info (adjust as needed)
REPO_FILE="/root/.restic-repo"
PASS_FILE="/root/.restic-password"

# Paths to back up
BACKUP_PATHS=(
  "/root"
  "/home"
  "/var"
  "/etc"
  "/srv"
  "/usr"
  "/opt"
  "/var/lib/docker/volumes"  # Docker volumes (local driver) 
)

echo "=== Stopping Docker to ensure data consistency ==="
sudo systemctl stop docker

echo "=== Running backup with Restic ==="
sudo restic \
  --repository-file "${REPO_FILE}" \
  --password-file "${PASS_FILE}" \
  --verbose \
  backup "${BACKUP_PATHS[@]}"

echo "=== Backup complete. Checking snapshots ==="
sudo restic \
  --repository-file "${REPO_FILE}" \
  --password-file "${PASS_FILE}" \
  snapshots

echo "=== Restarting Docker ==="
sudo systemctl start docker

echo "=== Done. Docker is back online. ==="