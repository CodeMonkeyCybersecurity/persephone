package main

import (
	"fmt"
	"log"
	"os/exec"
	"time"
)

func main() {
	// Calculate the next full hour
	now := time.Now()
	nextHour := now.Truncate(time.Hour).Add(time.Hour)
	startTime := nextHour.Format("15:04") // 24-hour format (HH:MM)

	// Define the scheduled task parameters
	taskName := "ResticBackupHourly"
	// Adjust the path to your backup script accordingly
	taskAction := `powershell.exe -NoProfile -ExecutionPolicy Bypass -File "C:\Scripts\backup.ps1"`

	// Build the schtasks command with required arguments:
	// /create - create a new task
	// /tn    - task name
	// /tr    - task to run
	// /sc    - schedule (hourly)
	// /ST    - start time (HH:MM format)
	cmd := exec.Command("schtasks",
		"/create",
		"/tn", taskName,
		"/tr", taskAction,
		"/sc", "hourly",
		"/ST", startTime,
	)

	// Execute the command
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Fatalf("Failed to create scheduled task: %v\nOutput: %s", err, string(output))
	}

	fmt.Printf("Scheduled task '%s' created successfully. Output:\n%s", taskName, string(output))
}
