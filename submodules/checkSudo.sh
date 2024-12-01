#!/usr/bin/env python3

import os
import sys

def check_sudo():
    """Check if the script is running as root."""
    if os.geteuid() != 0:
        print("\033[31m✘ This script must be run as root. Please use sudo.\033[0m")
        sys.exit(1)
    else:
        print("\033[32m✔ Running as root.\033[0m")

def main():
    """Main function to execute the script logic."""
    check_sudo()
    # Add additional logic here if needed
    print("Main script logic goes here.")

if __name__ == "__main__":
    main()
