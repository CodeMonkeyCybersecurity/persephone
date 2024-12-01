#!/usr/bin/env python3

import subprocess

def main():
    try:
        # Run the `df -h /` command and capture its output
        result = subprocess.run(["df", "-h", "/"], text=True, capture_output=True, check=True)
        stdout = result.stdout

        # Parse the output
        lines = stdout.strip().split("\n")
        root_line = lines[1].split()  # Second line corresponds to `/`

        # Extract the "Used" and "Available" values
        used = root_line[2]  # Third column is "Used"
        available = root_line[3]  # Fourth column is "Available"

        # Output the result
        print(f"Total Disk Usage: {used}")
        print(f"Total Disk Available: {available}")

    except subprocess.CalledProcessError as e:
        print(f"Error running df command: {e}")

if __name__ == "__main__":
    main()
