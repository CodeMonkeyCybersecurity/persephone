#!/usr/bin/env bash
#
# createPersephoneBackup.sh

set -euo pipefail

# -----------------------------
# Directories and Config
# -----------------------------
# Feel free to adjust these if you want a custom backup set
BACKUP_PATHS=(
  "/root"
  "/home"
  "/var"
  "/etc"
  "/srv"
  "/usr"
  "/opt"
)

REPO_FILE="/root/.restic-repo"
PASS_FILE="/root/.restic-password"

# -----------------------------
# Main Script
# -----------------------------
echo "Running Restic backup..."

sudo restic \
  --repository-file "${REPO_FILE}" \
  --password-file "${PASS_FILE}" \
  --verbose \
  backup "${BACKUP_PATHS[@]}"

echo "Backup completed. Checking snapshots..."

sudo restic \
  --repository-file "${REPO_FILE}" \
  --password-file "${PASS_FILE}" \
  snapshots

echo "Restic backup and snapshot check complete."