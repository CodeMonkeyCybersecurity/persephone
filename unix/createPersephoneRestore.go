package main

import (
	"bufio"
	"encoding/json"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"strconv"
	"strings"

	"golang.org/x/term"
)

const CONFIG_FILE = ".persephone.conf"

// Snapshot represents a restic snapshot.
type Snapshot struct {
	ShortID string   `json:"short_id"`
	Time    string   `json:"time"`
	Paths   []string `json:"paths"`
}

func checkResticInstalled() {
	cmd := exec.Command("which", "restic")
	err := cmd.Run()
	if err != nil {
		log.Fatal("Error: Restic is not installed or not in PATH.")
	}
}

func checkSudoPermissions() {
	cmd := exec.Command("sudo", "-n", "true")
	err := cmd.Run()
	if err != nil {
		log.Fatal("Error: This script requires sudo privileges, but `sudo` requires a password.")
	}
}

// loadConfig reads a config file (key="value" per line) and returns a map.
func loadConfig(configFile string) (map[string]string, error) {
	config := make(map[string]string)
	if _, err := os.Stat(configFile); os.IsNotExist(err) {
		return config, nil
	}

	data, err := ioutil.ReadFile(configFile)
	if err != nil {
		return nil, err
	}

	lines := strings.Split(string(data), "\n")
	for _, line := range lines {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		if idx := strings.Index(line, "="); idx != -1 {
			key := strings.TrimSpace(line[:idx])
			val := strings.TrimSpace(line[idx+1:])
			// Remove surrounding quotes.
			val = strings.Trim(val, `"'`)
			config[key] = val
		}
	}
	return config, nil
}

// saveConfig writes the config map to a file.
func saveConfig(configFile string, config map[string]string) error {
	var lines []string
	for key, value := range config {
		lines = append(lines, fmt.Sprintf(`%s="%s"`, key, value))
	}
	data := strings.Join(lines, "\n")
	err := ioutil.WriteFile(configFile, []byte(data), 0644)
	if err != nil {
		log.Fatalf("Error writing to config file: %v", err)
	}
	return nil
}

// promptInput prompts the user for input with an optional default value.
// If hidden is true, input is read without echoing.
func promptInput(promptMessage, defaultVal string, hidden bool) string {
	reader := bufio.NewReader(os.Stdin)
	var prompt string
	if defaultVal != "" {
		prompt = fmt.Sprintf("%s [%s]: ", promptMessage, defaultVal)
	} else {
		prompt = fmt.Sprintf("%s: ", promptMessage)
	}
	for {
		if hidden {
			fmt.Print(prompt)
			byteInput, err := term.ReadPassword(int(os.Stdin.Fd()))
			fmt.Println()
			if err != nil {
				log.Printf("Error reading hidden input: %v", err)
				continue
			}
			input := strings.TrimSpace(string(byteInput))
			if input == "" && defaultVal != "" {
				return defaultVal
			} else if input != "" {
				return input
			}
		} else {
			fmt.Print(prompt)
			text, err := reader.ReadString('\n')
			if err != nil {
				log.Printf("Error reading input: %v", err)
				continue
			}
			input := strings.TrimSpace(text)
			if input == "" && defaultVal != "" {
				return defaultVal
			} else if input != "" {
				return input
			}
		}
		fmt.Println("Error: Input cannot be empty. Please enter a valid value.")
	}
}

// ensureConfig checks if required values exist in the config, prompting the user if missing.
func ensureConfig(config map[string]string) map[string]string {
	requiredKeys := []string{"PERS_REPO_FILE", "PERS_PASSWD_FILE", "PERS_REPO_FILE_VALUE", "PERS_PASSWD_FILE_VALUE"}
	for _, key := range requiredKeys {
		if _, exists := config[key]; !exists || config[key] == "" {
			hidden := key == "PERS_PASSWD_FILE_VALUE" // Hide password input
			config[key] = promptInput(fmt.Sprintf("Enter value for %s", key), "", hidden)
		}
	}
	// Save any new values added
	saveConfig(CONFIG_FILE, config)
	return config
}



// listSnapshots calls restic to list snapshots (in JSON format) and returns the snapshots.
func listSnapshots(repoFile, passFile string) ([]Snapshot, error) {
    // Ensure files exist
    if _, err := os.Stat(repoFile); os.IsNotExist(err) {
        log.Fatalf("Error: Repository file %s does not exist.", repoFile)
    }
    if _, err := os.Stat(passFile); os.IsNotExist(err) {
        log.Fatalf("Error: Password file %s does not exist.", passFile)
    }

    // Ensure files are not empty
    repoContent, _ := ioutil.ReadFile(repoFile)
    passContent, _ := ioutil.ReadFile(passFile)
    if len(strings.TrimSpace(string(repoContent))) == 0 {
        log.Fatalf("Error: Repository file %s is empty.", repoFile)
    }
    if len(strings.TrimSpace(string(passContent))) == 0 {
        log.Fatalf("Error: Password file %s is empty.", passFile)
    }

    cmd := exec.Command("sudo", "restic",
        "--repository-file", repoFile,
        "--password-file", passFile,
        "snapshots", "--json",
    )

    output, err := cmd.CombinedOutput()
    if err != nil {
        log.Fatalf("Error retrieving snapshots: %v\nFull Output:\n%s", err, string(output))
    }

    fmt.Println("Raw restic snapshots output:", string(output)) // Debugging output

    var snapshots []Snapshot
    err = json.Unmarshal(output, &snapshots)
    if err != nil {
        log.Fatalf("Error parsing JSON: %v\nRestic Output: %s", err, string(output))
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

	// Double-check that the snapshot exists before restoring
	if snapshotID == "" {
		log.Fatal("Error: Invalid snapshot ID. Cannot restore.")
	}
	
	fmt.Printf("Are you sure you want to restore this snapshot? This may overwrite existing files. (y/N): ")
	confirm, _ := reader.ReadString('\n')
	confirm = strings.ToLower(strings.TrimSpace(confirm))
	if confirm != "y" && confirm != "yes" {
		fmt.Println("Restoration canceled.")
		os.Exit(0)
	}

	fmt.Printf("Running: sudo restic --repository-file=%s --password-file=%s restore %s --target=/\n", repoFile, passFile, snapshotID)
	
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

	// Update last restored snapshot in the config
	config, _ := loadConfig(CONFIG_FILE)
	config["LAST_RESTORED"] = snapshotID
	saveConfig(CONFIG_FILE, config)
}

func main() {
	checkResticInstalled()  // Ensure Restic is available
	checkSudoPermissions()   // Ensure sudo works without password prompt
	
	// Load configuration.
	config, err := loadConfig(CONFIG_FILE)
	if err != nil {
		log.Fatalf("Error loading config: %v\n", err)
	}

	// Ensure required config values exist.
	config = ensureConfig(config)

	repoFile := config["PERS_REPO_FILE"]
	passFile := config["PERS_PASSWD_FILE"]

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
