package main

import (
	"bufio"
	"bytes"
	"fmt"
	"io/ioutil"
	"math/rand"
	"os"
	"os/exec"
	"strings"
	"time"
)

// loadCrontab returns the current crontab as a slice of lines.
func loadCrontab() []string {
	cmd := exec.Command("crontab", "-l")
	output, err := cmd.Output()
	if err != nil {
		// If there is no crontab, return an empty slice.
		return []string{}
	}
	return strings.Split(string(output), "\n")
}

// backupCrontab backs up the current crontab to a file with a timestamp.
func backupCrontab(lines []string) {
	timestamp := time.Now().Format("20060102_150405")
	backupFilename := fmt.Sprintf("crontab_backup_%s.txt", timestamp)
	data := strings.Join(lines, "\n") + "\n"
	if err := ioutil.WriteFile(backupFilename, []byte(data), 0644); err != nil {
		fmt.Printf("Error backing up crontab: %v\n", err)
	} else {
		fmt.Printf("Crontab backed up to %s\n", backupFilename)
	}
}

// removePersephoneLines returns a new slice of lines with any non-comment lines
// containing "persephone" removed and also returns the removed lines.
func removePersephoneLines(lines []string) (newLines []string, removed []string) {
	for _, line := range lines {
		trimmed := strings.TrimSpace(line)
		if trimmed != "" && !strings.HasPrefix(trimmed, "#") && strings.Contains(trimmed, "persephone") {
			removed = append(removed, line)
		} else {
			newLines = append(newLines, line)
		}
	}
	return newLines, removed
}

// promptInput prompts the user for input and returns the response.
// If the response is empty, it returns the defaultVal.
func promptInput(promptMessage string, defaultVal string) string {
	reader := bufio.NewReader(os.Stdin)
	var prompt string
	if defaultVal != "" {
		prompt = fmt.Sprintf("%s [%s]: ", promptMessage, defaultVal)
	} else {
		prompt = fmt.Sprintf("%s: ", promptMessage)
	}
	fmt.Print(prompt)
	resp, _ := reader.ReadString('\n')
	resp = strings.TrimSpace(resp)
	if resp == "" {
		return defaultVal
	}
	return resp
}

// getCronSchedule prompts the user for a cron schedule (5 fields) and returns them.
// The default schedule is set to hourly: "0 * * * *"
func getCronSchedule() []string {
	for {
		schedule := promptInput("Enter cron schedule (minute hour day-of-month month day-of-week)", "0 * * * *")
		fields := strings.Fields(schedule)
		if len(fields) == 5 {
			return fields
		}
		fmt.Println("Invalid schedule. Please enter exactly 5 space-separated fields (e.g., '0 2 * * *').")
	}
}

func main() {
	// Load current crontab and back it up.
	currentCron := loadCrontab()
	backupCrontab(currentCron)

	// Check for any lines containing "persephone" and remove them.
	newCron, removed := removePersephoneLines(currentCron)
	if len(removed) > 0 {
		fmt.Println("\nFound the following persephone-related lines in your crontab:")
		for _, line := range removed {
			fmt.Println("  " + line)
		}
		choice := promptInput("Do you want to delete these lines? (Y/n)", "Y")
		if !(strings.EqualFold(choice, "y") || strings.EqualFold(choice, "yes") || choice == "") {
			fmt.Println("WARNING: Multiple persephone lines in the crontab may lead to undesired outcomes.")
		} else {
			currentCron = newCron
		}
	}

	// Prompt for a new cron schedule.
	cronFields := getCronSchedule()

	// Ask if the minute field should be randomized.
	randChoice := promptInput("Randomize the minute field? (Y/n)", "Y")
	if strings.EqualFold(randChoice, "y") || strings.EqualFold(randChoice, "yes") {
		rand.Seed(time.Now().UnixNano())
		randomMinute := fmt.Sprintf("%d", rand.Intn(60))
		cronFields[0] = randomMinute
		fmt.Printf("Minute field randomized to %s\n", randomMinute)
	}
	newSchedule := strings.Join(cronFields, " ")

	// Build the new cron line.
	newCronLine := fmt.Sprintf("%s /opt/persephone/persephone.sh", newSchedule)
	fmt.Println("\nNew cron line to be added:")
	fmt.Println(newCronLine)

	// Append the new cron line to the current crontab lines.
	currentCron = append(currentCron, newCronLine)
	newCronContent := strings.Join(currentCron, "\n") + "\n"

	// Update the crontab.
	cmd := exec.Command("crontab", "-")
	cmd.Stdin = bytes.NewBufferString(newCronContent)
	if output, err := cmd.CombinedOutput(); err != nil {
		fmt.Printf("Error updating crontab: %v\nOutput: %s\n", err, string(output))
		return
	}

	// Display the updated crontab.
	fmt.Println("\nCrontab updated successfully. New crontab:")
	listCmd := exec.Command("crontab", "-l")
	listOut, err := listCmd.CombinedOutput()
	if err != nil {
		fmt.Printf("Error listing crontab: %v\n", err)
	} else {
		fmt.Println(string(listOut))
	}
	fmt.Println("\nPlease confirm this works by running /opt/persephone/persephone.sh in your terminal.")
}
