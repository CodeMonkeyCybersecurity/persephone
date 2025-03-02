package main

import (
	"fmt"
	"log"
	"os/exec"
)

func main() {
	// Set these values as appropriate for your environment.
	// Use forward slashes in paths for consistency.
	repo := "s3:https://persephoneapi.cybermonkey.dev/restic/H-Windows"
	passFile := `C:/opt/persephone/windows/persephone-passwd.txt`
	// List the backup paths along with exclude flags as separate arguments.
	// Note: Adjust the paths/exclusions to match what you want to exclude.
	args := []string{
		"--repo", repo,
		"--password-file", passFile,
		"backup",
		"--dry-run",
		"C:/Users",
		"C:/ProgramData",
		"C:/Windows",
		"--exclude", "C:/Users/*/AppData/Local/Temp",
		"--exclude", "C:/Windows/Temp",
		"--exclude", "C:/Windows/WinSxS",
		"--exclude", "C:/Users/*/Nextcloud",
		"--exclude", "C:/Users/*/OneDrive",
	}

	// Execute the restic backup command in dry-run mode.
	cmd := exec.Command("restic", args...)
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Fatalf("Dry-run backup failed: %v\nOutput:\n%s", err, string(output))
	}

	fmt.Println("Dry-run backup output:")
	fmt.Println(string(output))
}
