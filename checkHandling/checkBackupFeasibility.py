#!/usr/bin/env python3

import subprocess
import re

def runCommand(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error: Command '{command}' failed with error: {e.stderr}")
        return None

def convertToGb(size):
    """Convert a size string (e.g., '10G', '1.5T') to GB."""
    size = size.replace(',', '')  # Remove commas
    if size.endswith('G'):
        return float(size[:-1])
    if size.endswith('T'):
        return float(size[:-1]) * 1024
    return 0  # Return 0 if unhandled case

def checkBackupFeasibility():
    """Check if there is enough space for a Docker backup."""
    # Run the checkDiskUsage.mjs script
    disk_usage_output = run_command("zx checkDiskUsage.mjs")
    if not disk_usage_output:
        print("Error: Could not retrieve disk usage.")
        return

    available_disk_match = re.search(r"Total Disk Available: (\d+(\.\d+)?[A-Z])", disk_usage_output)
    available_disk = available_disk_match.group(1) if available_disk_match else None

    # Run the checkDockerDiskUsage.mjs script
    docker_usage_output = run_command("zx checkDockerDiskUsage.mjs")
    if not docker_usage_output:
        print("Error: Could not retrieve Docker disk usage.")
        return

    safe_backup_match = re.search(r"Total space required for safe Docker backup: (\d+(\.\d+)? [A-Z]+)", docker_usage_output)
    safe_backup_size = safe_backup_match.group(1) if safe_backup_match else None

    if not available_disk or not safe_backup_size:
        print("Error: Could not extract disk usage or safe backup size.")
        return

    # Convert to GB
    available_disk_gb = convert_to_gb(available_disk)
    safe_backup_size_gb = convert_to_gb(safe_backup_size)

    # Determine if backup is feasible
    is_feasible = available_disk_gb > safe_backup_size_gb
    print(f"Is there enough space for the Docker backup? {is_feasible}")

if __name__ == "__main__":
    checkBackupFeasibility()
