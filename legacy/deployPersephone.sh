#!/usr/bin/env bash
#
# install_dependencies.sh

set -euo pipefail

# -----------------------------
# Main Script
# -----------------------------
echo "Installing dependencies..."

# Update package lists
sudo apt-get update

# Install Restic
echo "Installing Restic..."
sudo apt-get install -y restic

echo "Dependencies installed successfully."
