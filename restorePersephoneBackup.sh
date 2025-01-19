#!/bin/bash
#
# restorePersephoneBackup.sh

set -euo pipefail

# -----------------------------
# Directories and Config
# -----------------------------

echo "Checking Restic backup and snapshots."

REPO_FILE="/root/.restic-repo"
PASS_FILE="/root/.restic-password"

sudo restic \
  --repository-file "${REPO_FILE}" \
  --password-file "${PASS_FILE}" \
  snapshots

echo "Restic backup and snapshot check complete."

# -----------------------------
# Main Script
# -----------------------------
# TODO complete main script

