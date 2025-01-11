#!/usr/bin/env python3

import subprocess

def run_command(command):
    """Run a shell command and return its output."""
    try:
        result = subprocess.run(command, shell=True, text=True, capture_output=True, check=True)
        return result.stdout
    except subprocess.CalledProcessError as e:
        print(f"Error running command '{command}': {e.stderr}")
        return None

def main():
    try:
        # Run the `df -h /` command and capture its output
        df_output = run_command("df -h /")
        if df_output:
            lines = df_output.strip().split("\n")
            root_line = lines[1].split()  # Second line corresponds to `/`

            # Extract the "Used" and "Available" values
            used = root_line[2]  # Third column is "Used"
            available = root_line[3]  # Fourth column is "Available"

            print(f"Total Disk Usage: {used}")
            print(f"Total Disk Available: {available}")

        # Run the `lsblk` command to list block devices
        lsblk_output = run_command("lsblk")
        if lsblk_output:
            print("\nBlock Devices:")
            print(lsblk_output)

        # Run the `pvs` command to list physical volumes
        pvs_output = run_command("sudo pvs")
        if pvs_output:
            print("\nPhysical Volumes:")
            print(pvs_output)

        # Run the `vgs` command to list volume groups
        vgs_output = run_command("sudo vgs")
        if vgs_output:
            print("\nVolume Groups:")
            print(vgs_output)

        # Run the `lvs` command to list logical volumes
        lvs_output = run_command("sudo lvs")
        if lvs_output:
            print("\nLogical Volumes:")
            print(lvs_output)

        print("done")

    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    main()
