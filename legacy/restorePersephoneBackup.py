#!/usr/bin/env python3
"""
restorePersephoneBackup.py

This script restores a Restic backup snapshot. It loads configuration values
from .persephone_backup.conf (which should define REPO_FILE and PASS_FILE),
lists available snapshots by calling Restic (parsing its JSON output), prompts
the user to select a snapshot, and then performs the restore.

Note: This script requires that Restic is installed and available on the system.
It uses sudo to run Restic commands.
"""

import os
import subprocess
import json
import sys

CONFIG_FILE = ".persephone_backup.conf"

def load_config(config_file):
    """
    Loads configuration from the given file.
    Expected format: one key="value" per line.
    Returns a dictionary.
    """
    config = {}
    if os.path.exists(config_file):
        with open(config_file, "r") as f:
            for line in f:
                line = line.strip()
                if not line or line.startswith("#"):
                    continue
                if "=" in line:
                    key, value = line.split("=", 1)
                    key = key.strip()
                    value = value.strip().strip('"').strip("'")
                    config[key] = value
    else:
        print(f"Configuration file {config_file} not found. Exiting.")
        sys.exit(1)
    return config

def list_snapshots(repo_file, pass_file):
    """
    Calls restic to list snapshots in JSON format and returns a list of snapshot dictionaries.
    Each dictionary is expected to have at least keys: 'short_id', 'time', and 'paths'.
    """
    try:
        result = subprocess.run(
            ["sudo", "restic",
             "--repository-file", repo_file,
             "--password-file", pass_file,
             "snapshots", "--json"],
            capture_output=True, text=True, check=True
        )
        snapshots = json.loads(result.stdout)
        return snapshots
    except subprocess.CalledProcessError as e:
        print("Error retrieving snapshots:", e)
        sys.exit(1)
    except json.JSONDecodeError as e:
        print("Error parsing JSON output from restic:", e)
        sys.exit(1)

def display_snapshots(snapshots):
    """
    Displays a numbered list of snapshots. For each snapshot, shows:
      short_id, time, and the first path from the list of paths.
    Returns a list of snapshot short_ids corresponding to the displayed order.
    """
    if not snapshots:
        print("No snapshots found.")
        sys.exit(1)
    snapshot_ids = []
    print("Available Snapshots:")
    print("-------------------")
    for idx, snap in enumerate(snapshots, start=1):
        short_id = snap.get("short_id", "unknown")
        snap_time = snap.get("time", "unknown")
        paths = snap.get("paths", [])
        path_display = paths[0] if paths else "N/A"
        print(f"{idx:3d}) {short_id} {snap_time} {path_display}")
        snapshot_ids.append(short_id)
    print()
    return snapshot_ids

def select_snapshot(snapshot_ids):
    """
    Prompts the user to select a snapshot number from the provided list.
    Returns the snapshot short_id corresponding to the user's choice.
    """
    while True:
        selection = input("Enter the number of the snapshot you want to restore: ").strip()
        if selection.isdigit():
            index = int(selection)
            if 1 <= index <= len(snapshot_ids):
                selected_snapshot = snapshot_ids[index - 1]
                print(f"You have selected snapshot: {selected_snapshot}")
                return selected_snapshot
        print(f"Invalid selection. Please enter a number between 1 and {len(snapshot_ids)}.")

def restore_snapshot(repo_file, pass_file, snapshot_id):
    """
    Prompts the user for confirmation and then runs the restic restore command for the selected snapshot.
    """
    print(f"Starting restoration process for snapshot {snapshot_id}...")
    confirm = input("Are you sure you want to restore this snapshot? This may overwrite existing files. (y/N): ").strip().lower()
    if confirm not in ["y", "yes"]:
        print("Restoration canceled.")
        sys.exit(0)

    try:
        subprocess.run(
            ["sudo", "restic",
             "--repository-file", repo_file,
             "--password-file", pass_file,
             "restore", snapshot_id, "--target", "/"],
            check=True
        )
        print(f"Restoration of snapshot {snapshot_id} completed successfully.")
    except subprocess.CalledProcessError as e:
        print("Error during restoration:", e)
        sys.exit(1)

def main():
    # Load configuration
    config = load_config(CONFIG_FILE)
    repo_file = config.get("REPO_FILE")
    pass_file = config.get("PASS_FILE")
    if not repo_file or not pass_file:
        print("Missing REPO_FILE or PASS_FILE in configuration. Exiting.")
        sys.exit(1)

    print("Checking Restic backup and snapshots...\n")

    # List snapshots and prompt for selection.
    snapshots = list_snapshots(repo_file, pass_file)
    snapshot_ids = display_snapshots(snapshots)
    selected_snapshot = select_snapshot(snapshot_ids)
    
    # Restore the selected snapshot.
    restore_snapshot(repo_file, pass_file, selected_snapshot)
    print("Restic restore process complete.")

if __name__ == "__main__":
    main()
