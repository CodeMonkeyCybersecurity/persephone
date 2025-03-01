package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"log"
	"os"
	"os/exec"
	"strconv"
	"strings"
)

const CONFIG_FILE = ".persephone_backup.conf"

// Snapshot represents a restic snapshot.
type Snapshot struct {
	ShortID string   `json:"short_id"`
	Time    string   `json:"time"`
	Paths   []string `json:"paths"`
}

// loadConfig loads configuration from a file with one key="value" per line.
func loadConfig(configFile string) (map[string]string, error) {
	config := make(map[string]string)
	file, err := os.Open(configFile)
	if err != nil {
		return nil, fmt.Errorf("configuration file %s not found", configFile)
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		if idx := strings.Index(line, "="); idx != -1 {
			key := strings.TrimSpace(line[:idx])
			val := strings.TrimSpace(line[idx+1:])
			// Remove surrounding quotes if any.
			val = strings.Trim(val, `"'`)
			config[key] = val
		}
	}
	if err := scanner.Err(); err != nil {
		return nil, err
	}
	return config, nil
}

// listSnapshots calls restic to list snapshots (in JSON format) and returns the snapshots.
func listSnapshots(repoFile, passFile string) ([]Snapshot, error) {
	cmd := exec.Command("sudo", "restic",
		"--repository-file", repoFile,
		"--password-file", passFile,
		"snapshots", "--json",
	)
	output, err := cmd.Output()
	if err != nil {
		return nil, fmt.Errorf("error retrieving snapshots: %v", err)
	}

	var snapshots []Snapshot
	if err := json.Unmarshal(output, &snapshots); err != nil {
		return nil, fmt.Errorf("error parsing JSON output from restic: %v", err)
	}
	return snapshots, nil
}

// displaySnapshots prints a numbered list of snapshots.
// Returns a slice of snapshot short IDs in the displayed order.
func displaySnapshots(snapshots []Snapshot) []string {
	if len(snapshots) == 0 {
		log.Fatal("No snapshots found.")
	}

	var snapshotIDs []string
	fmt.Println("Available Snapshots:")
	fmt.Println("--------------------")
	for idx, snap := range snapshots {
		shortID := snap.ShortID
		snapTime := snap.Time
		pathDisplay := "N/A"
		if len(snap.Paths) > 0 {
			pathDisplay = snap.Paths[0]
		}
		fmt.Printf("%3d) %s  %s  %s\n", idx+1, shortID, snapTime, pathDisplay)
		snapshotIDs = append(snapshotIDs, shortID)
	}
	fmt.Println()
	return snapshotIDs
}

// selectSnapshot prompts the user to choose a snapshot number.
// Returns the corresponding snapshot short ID.
func selectSnapshot(snapshotIDs []string) string {
	reader := bufio.NewReader(os.Stdin)
	for {
		fmt.Printf("Enter the number of the snapshot you want to restore: ")
		input, _ := reader.ReadString('\n')
		input = strings.TrimSpace(input)
		if num, err := strconv.Atoi(input); err == nil {
			if num >= 1 && num <= len(snapshotIDs) {
				selected := snapshotIDs[num-1]
				fmt.Printf("You have selected snapshot: %s\n", selected)
				return selected
			}
		}
		fmt.Printf("Invalid selection. Please enter a number between 1 and %d.\n", len(snapshotIDs))
	}
}

// restoreSnapshot prompts for confirmation and then restores the selected snapshot.
func restoreSnapshot(repoFile, passFile, snapshotID string) {
	reader := bufio.NewReader(os.Stdin)
	fmt.Printf("Starting restoration process for snapshot %s...\n", snapshotID)
	fmt.Printf("Are you sure you want to restore this snapshot? This may overwrite existing files. (y/N): ")
	confirm, _ := reader.ReadString('\n')
	confirm = strings.ToLower(strings.TrimSpace(confirm))
	if confirm != "y" && confirm != "yes" {
		fmt.Println("Restoration canceled.")
		os.Exit(0)
	}

	cmd := exec.Command("sudo", "restic",
		"--repository-file", repoFile,
		"--password-file", passFile,
		"restore", snapshotID, "--target", "/",
	)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		log.Fatalf("Error during restoration: %v", err)
	}
	fmt.Printf("Restoration of snapshot %s completed successfully.\n", snapshotID)
}

func main() {
	// Load configuration.
	config, err := loadConfig(CONFIG_FILE)
	if err != nil {
		log.Fatalf("Error loading config: %v\n", err)
	}
	repoFile, repoOk := config["REPO_FILE"]
	passFile, passOk := config["PASS_FILE"]
	if !repoOk || !passOk {
		log.Fatal("Missing REPO_FILE or PASS_FILE in configuration. Exiting.")
	}

	fmt.Println("Checking Restic backup and snapshots...\n")

	// List snapshots.
	snapshots, err := listSnapshots(repoFile, passFile)
	if err != nil {
		log.Fatalf("%v", err)
	}

	// Display snapshots and prompt for selection.
	snapshotIDs := displaySnapshots(snapshots)
	selectedSnapshot := selectSnapshot(snapshotIDs)

	// Restore the selected snapshot.
	restoreSnapshot(repoFile, passFile, selectedSnapshot)
	fmt.Println("Restic restore process complete.")
}
