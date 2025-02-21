#!/usr/bin/env python3
"""
createPersephonRepoSFTP.py

This script sets up a backup repository on the server by:
  - Creating the designated server directory for backups.
  - Securing the directory with restricted permissions and ownership.
  - Printing out server information for future reference.
"""

import os
import subprocess
import getpass
import socket

# -----------------------------
# Directories
# -----------------------------
SRV_DIR = '/srv/codeMonkeyCyber'  # Directory where Restic repos will live
LOG_DIR = '/var/log/codeMonkeyCyber'  # Log directory (not used further here)

def run_command(cmd):
    """Runs a command with subprocess, propagating errors if any occur."""
    subprocess.run(cmd, check=True)

def main():
    print("Setting up backup repository on server...\n")
    
    # 1. Create server directory for backups.
    run_command(["sudo", "mkdir", "-p", SRV_DIR])
    
    # 2. Secure ownership & permissions.
    run_command(["sudo", "chown", "-R", "root:root", SRV_DIR])
    # 700 ensures only root can access the directory.
    run_command(["sudo", "chmod", "600", SRV_DIR])
    
    print(f"Server repository directory set up at {SRV_DIR} with restricted permissions.\n")
    
    # Get server user and hostname.
    pers_srv_user = getpass.getuser()
    pers_srv_hostname = socket.gethostname()
    
    print(f"This server is located at {pers_srv_user}@{pers_srv_hostname}:{SRV_DIR}")
    print("It is important you note this down somewhere.")
    print("You will use it when running `./createPersephoneClient.sh`")
    print("It's also generally a good idea to know where your backups are stored.")

if __name__ == "__main__":
    main()
