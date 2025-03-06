package main

import (
	"fmt"
	"os"
	"os/exec"
	"strings"
)

// checkCommand checks if a command is available in PATH
func checkCommand(cmd string) bool {
	_, err := exec.LookPath(cmd)
	return err == nil
}

// runCommand executes a shell command and outputs progress
func runCommand(name string, args ...string) error {
	cmd := exec.Command(name, args...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		return fmt.Errorf("command failed: %v", err)
	}
	return nil
}

// detectPackageManager detects whether apt or yum is available
func detectPackageManager() string {
	if checkCommand("apt") {
		return "apt"
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
		fmt.Println("No supported package manager found (apt or yum). Exiting.")
		os.Exit(1)
	}

	var installCmd []string
	if pm == "apt" {
		installCmd = []string{"apt", "update", "&&", "apt", "install", "-y", "restic"}
	} else {
		installCmd = []string{"yum", "install", "-y", "restic"}
	}

	fmt.Printf("Using %s to install restic...\n", pm)
	if err := runCommand(installCmd[0], installCmd[1:]...); err != nil {
		fmt.Printf("Error installing restic: %v\n", err)
		os.Exit(1)
	}

	if checkCommand("restic") {
		fmt.Println("Restic installed successfully.")
	} else {
		fmt.Println("Restic installation failed.")
		os.Exit(1)
	}

	fmt.Println("finis")
}
