#!/usr/bin/env python3
import subprocess
import sys
import os

def list_volumes():
    """
    Returns a list of Docker volume names.
    """
    try:
        result = subprocess.run(
            ["docker", "volume", "ls", "--format", "{{.Name}}"],
            capture_output=True,
            text=True,
            check=True
        )
        volumes = result.stdout.splitlines()
        return volumes
    except subprocess.CalledProcessError as e:
        print("Error listing volumes:", e, file=sys.stderr)
        sys.exit(1)

def check_running_containers():
    """
    Checks if any Docker containers are running.
    Exits if there are any.
    """
    try:
        result = subprocess.run(
            ["docker", "ps", "-q"],
            capture_output=True,
            text=True,
            check=True
        )
        container_ids = result.stdout.splitlines()
        if container_ids:
            print("There are running containers. Please stop all running containers before running the backup.", file=sys.stderr)
            sys.exit(1)
    except subprocess.CalledProcessError as e:
        print("Error checking running containers:", e, file=sys.stderr)
        sys.exit(1)

def backup_volume(volume_name, backup_dir):
    """
    Backs up the specified Docker volume using the loomchild/volume-backup container.
    The backup archive is stored as <backup_dir>/<volume_name>.tar.
    """
    archive_path = os.path.join(backup_dir, f"{volume_name}.tar")
    print(f"Backing up volume '{volume_name}' to '{archive_path}'...")

    # Build the docker command:
    # docker run -v [volume-name]:/volume --rm --log-driver none loomchild/volume-backup backup
    command = [
        "docker", "run",
        "-v", f"{volume_name}:/volume",
        "--rm",
        "--log-driver", "none",
        "loomchild/volume-backup",
        "backup"
    ]

    try:
        # Open the archive file for writing binary data.
        with open(archive_path, "wb") as archive_file:
            # Run the command, writing stdout to the archive file.
            subprocess.run(command, stdout=archive_file, stderr=subprocess.PIPE, check=True)
    except subprocess.CalledProcessError as e:
        print(f"Error backing up volume '{volume_name}':", e, file=sys.stderr)
        sys.exit(1)

def main():
    # Check if any containers are running.
    check_running_containers()

    # List all docker volumes.
    volumes = list_volumes()
    if not volumes:
        print("No Docker volumes found.")
        sys.exit(0)

    # Create backup directory if it doesn't exist.
    backup_dir = "backups"
    if not os.path.exists(backup_dir):
        os.makedirs(backup_dir)

    # Iterate over each volume and back it up.
    for volume in volumes:
        backup_volume(volume, backup_dir)

    print("All backups completed successfully.")

if __name__ == '__main__':
    main()
