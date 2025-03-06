package main

import (
	"fmt"
	"os"
	"os/exec"
)

func checkCommand(cmd string) bool {
	_, err := exec.LookPath(cmd)
	return err == nil
}

func runCommand(name string, args ...string) error {
	cmd := exec.Command(name, args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func detectPackageManager() string {
	if checkCommand("apt-get") {
		return "apt-get"
	} else if checkCommand("yum") {
		return "yum"
	}
	return ""
}

func main() {
	fmt.Println("Checking if restic is installed...")

	if checkCommand("restic") {
		fmt.Println("Restic is already installed.")
		fmt.Println("finis")
		os.Exit(0)
	}

	fmt.Println("Restic not found. Installing...")
	pm := detectPackageManager()

	if pm == "" {
		fmt.Println("No supported package manager found (apt-get or yum). Exiting.")
		os.Exit(1)
	}

	fmt.Printf("Using %s to install restic...\n", pm)
	if pm == "apt-get" {
		if err := runCommand("apt-get", "update"); err != nil {
			fmt.Printf("Error updating package lists: %v\n", err)
			os.Exit(1)
		}
		if err := runCommand("apt-get", "install", "-y", "restic"); err != nil {
			fmt.Printf("Error installing restic: %v\n", err)
			os.Exit(1)
		}
	} else {
		if err := runCommand("yum", "install", "-y", "restic"); err != nil {
			fmt.Printf("Error installing restic: %v\n", err)
			os.Exit(1)
		}
	}

	if checkCommand("restic") {
		fmt.Println("Restic installed successfully.")
	} else {
		fmt.Println("Restic installation failed.")
		os.Exit(1)
	}

	fmt.Println("finis")
}
