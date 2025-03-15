package main

import (
	"bufio"
	"fmt"
	"io"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"golang.org/x/term"
)

const (
	CONFIG_FILE         = ".persephone.conf"
	BACKUP_SCRIPT_NAME  = "persephone.sh"
	INSPECT_SCRIPT_NAME = "persephoneInspectSnapshots.sh"
	TARGET_DIR          = "/opt/persephone/"
)

// loadConfig loads configuration from a file with one key="value" per line.
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
			val := strings.Trim(strings.TrimSpace(line[idx+1:]), `"'`)
			config[key] = val
		}
	}
	return config, nil
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
		fmt.Print(prompt)
		var input string
		if hidden {
			byteInput, err := term.ReadPassword(int(os.Stdin.Fd()))
			fmt.Println()
			if err != nil {
				log.Printf("Error reading input: %v", err)
				continue
			}
			input = strings.TrimSpace(string(byteInput))
		} else {
			text, err := reader.ReadString('\n')
			if err != nil {
				log.Printf("Error reading input: %v", err)
				continue
			}
			input = strings.TrimSpace(text)
		}

		if input == "" && defaultVal != "" {
			return defaultVal
		} else if input != "" {
			return input
		} else {
			fmt.Println("Error: Input cannot be empty. Please enter a valid value.")
		}
	}
}

// saveConfig writes the configuration to the config file.
func saveConfig(configFile string, config map[string]string) error {
	var lines []string
	for key, value := range config {
		lines = append(lines, fmt.Sprintf(`%s="%s"`, key, value))
	}
	data := strings.Join(lines, "\n")
	return ioutil.WriteFile(configFile, []byte(data), 0644)
}

// generateBashScript generates the backup bash script content with --verbose=2 flag.
func generateBashScript(config map[string]string) string {
	hostname, _ := os.Hostname()
	lines := []string{
		"#!/bin/bash",
		"",
		fmt.Sprintf("export AWS_ACCESS_KEY_ID=%s", config["AWS_ACCESS_KEY_ID"]),
		fmt.Sprintf("export AWS_SECRET_ACCESS_KEY=%s", config["AWS_SECRET_ACCESS_KEY"]),
		fmt.Sprintf("restic -r %s --password-file %s backup --verbose=2 %s --tag \"%s-$(date +\\%%Y-\\%%m-\\%%d_\\%%H-\\%%M-\\%%S)\"",
			config["PERS_REPO_FILE_VALUE"], config["PERS_PASSWD_FILE"], config["BACKUP_PATHS_STR"], hostname),
		`echo ""`,
		`echo "finis"`,
	}
	return strings.Join(lines, "\n")
}

// generateInspectScript generates the inspect snapshots bash script content with --verbose=2 flag.
func generateInspectScript(config map[string]string) string {
	lines := []string{
		"#!/bin/bash",
		"",
		fmt.Sprintf("export AWS_ACCESS_KEY_ID=%s", config["AWS_ACCESS_KEY_ID"]),
		fmt.Sprintf("export AWS_SECRET_ACCESS_KEY=%s", config["AWS_SECRET_ACCESS_KEY"]),
		// Note: Added --verbose=2 flag after snapshots.
		fmt.Sprintf("restic -r %s --password-file %s snapshots --verbose=2", config["PERS_REPO_FILE_VALUE"], config["PERS_PASSWD_FILE"]),
		`echo ""`,
		`echo "Inspection complete."`,
	}
	return strings.Join(lines, "\n")
}

// backupFile creates a timestamped backup of the given file if it exists.
func backupFile(filePath string) error {
	if _, err := os.Stat(filePath); err == nil {
		timestamp := time.Now().Format("20060102-150405")
		backupPath := fmt.Sprintf("%s.backup.%s", filePath, timestamp)
		fmt.Printf("Backing up %s to %s...\n", filePath, backupPath)
		// Copy the file.
		source, err := os.Open(filePath)
		if err != nil {
			return err
		}
		defer source.Close()
		dest, err := os.Create(backupPath)
		if err != nil {
			return err
		}
		defer dest.Close()
		if _, err := io.Copy(dest, source); err != nil {
			return err
		}
		fmt.Println("Backup complete.")
	}
	return nil
}

func main() {
	// Load existing configuration if available.
	config, err := loadConfig(CONFIG_FILE)
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	fmt.Println("=== Restic Backup Configuration ===")

	// --- Repository file and its literal value ---
	defaultRepoFile := "/root/.persephone-repo"
	if v, ok := config["PERS_REPO_FILE"]; ok && v != "" {
		defaultRepoFile = v
	}
	persRepoFile := promptInput("Enter the repository file path", defaultRepoFile, false)

	defaultRepoValue := "s3:https://persephoneapi.domain.com/repo-name/endpoint-name"
	if v, ok := config["PERS_REPO_FILE_VALUE"]; ok && v != "" {
		defaultRepoValue = v
	}
	persRepoFileValue := promptInput("Enter the repository file literal value", defaultRepoValue, false)

	// --- Password file and its literal value ---
	defaultPassFile := "/root/.persephone-passwd"
	if v, ok := config["PERS_PASSWD_FILE"]; ok && v != "" {
		defaultPassFile = v
	}
	persPassFile := promptInput("Enter the password file path", defaultPassFile, false)

	defaultPassValue := "default-password"
	if v, ok := config["PERS_PASSWD_FILE_VALUE"]; ok && v != "" {
		defaultPassValue = v
	}
	persPassValue := promptInput("Enter the password file literal value", defaultPassValue, true)

	// --- Other configuration values ---
	defaultBackupPaths := "/root /home /var /etc /srv /usr /opt"
	if v, ok := config["BACKUP_PATHS_STR"]; ok && v != "" {
		defaultBackupPaths = v
	}
	backupPathsStr := promptInput("Enter backup paths (space-separated)", defaultBackupPaths, false)

	defaultAWSAccessKey := ""
	if v, ok := config["AWS_ACCESS_KEY_ID"]; ok {
		defaultAWSAccessKey = v
	}
	awsAccessKey := promptInput("Enter AWS_ACCESS_KEY_ID", defaultAWSAccessKey, false)

	defaultAWSSecretKey := ""
	if v, ok := config["AWS_SECRET_ACCESS_KEY"]; ok {
		defaultAWSSecretKey = v
	}
	awsSecretKey := promptInput("Enter AWS_SECRET_ACCESS_KEY", defaultAWSSecretKey, true)

	// Update configuration map.
	config["PERS_REPO_FILE"] = persRepoFile
	config["PERS_REPO_FILE_VALUE"] = persRepoFileValue
	config["PERS_PASSWD_FILE"] = persPassFile
	config["PERS_PASSWD_FILE_VALUE"] = persPassValue
	config["BACKUP_PATHS_STR"] = backupPathsStr
	config["AWS_ACCESS_KEY_ID"] = awsAccessKey
	config["AWS_SECRET_ACCESS_KEY"] = awsSecretKey

	// Save the configuration for future runs.
	if err := saveConfig(CONFIG_FILE, config); err != nil {
		log.Fatalf("Error saving config: %v", err)
	}
	fmt.Printf("\nConfiguration successfully saved to %s\n", CONFIG_FILE)

	// Update repository file with the literal value.
	if err := ioutil.WriteFile(persRepoFile, []byte(persRepoFileValue+"\n"), 0644); err != nil {
		fmt.Printf("Error writing to %s: %v\n", persRepoFile, err)
	} else {
		fmt.Printf("Updated repository file at %s with the confirmed value.\n", persRepoFile)
	}

	// Update password file with the literal value.
	if err := ioutil.WriteFile(persPassFile, []byte(persPassValue+"\n"), 0644); err != nil {
		fmt.Printf("Error writing to %s: %v\n", persPassFile, err)
	} else {
		fmt.Printf("Updated password file at %s with the confirmed value.\n", persPassFile)
	}

	// Generate the backup bash script.
	backupScriptContent := generateBashScript(config)
	backupScriptPath := filepath.Join(".", BACKUP_SCRIPT_NAME)
	if err := ioutil.WriteFile(backupScriptPath, []byte(backupScriptContent+"\n"), 0755); err != nil {
		fmt.Printf("Error writing bash script: %v\n", err)
		return
	}
	fmt.Printf("\nBash script '%s' generated in current directory.\n", BACKUP_SCRIPT_NAME)

	// Generate the inspect snapshots bash script.
	inspectScriptContent := generateInspectScript(config)
	inspectScriptPath := filepath.Join(".", INSPECT_SCRIPT_NAME)
	if err := ioutil.WriteFile(inspectScriptPath, []byte(inspectScriptContent+"\n"), 0755); err != nil {
		fmt.Printf("Error writing inspect script: %v\n", err)
		return
	}
	fmt.Printf("Bash script '%s' generated in current directory.\n", INSPECT_SCRIPT_NAME)

	// Create target directory if it doesn't exist.
	if err := os.MkdirAll(TARGET_DIR, 0755); err != nil {
		fmt.Printf("Error creating target directory %s: %v\n", TARGET_DIR, err)
		return
	}

	// Move the scripts to the target directory.
	targetBackupPath := filepath.Join(TARGET_DIR, BACKUP_SCRIPT_NAME)
	targetInspectPath := filepath.Join(TARGET_DIR, INSPECT_SCRIPT_NAME)
	if err := os.Rename(backupScriptPath, targetBackupPath); err != nil {
		fmt.Printf("Error moving backup script: %v\n", err)
		return
	}
	if err := os.Rename(inspectScriptPath, targetInspectPath); err != nil {
		fmt.Printf("Error moving inspect script: %v\n", err)
		return
	}
	fmt.Printf("Bash scripts moved to: %s\n\n", TARGET_DIR)
	fmt.Printf("Please run %s to check the backup script works correctly.\n", targetBackupPath)
	fmt.Printf("And run %s to inspect your Persephone snapshots.\n\n", targetInspectPath)
	fmt.Println("If everything works correctly, consider running 'go run createPersephoneSchedule.go' to set up automated backups.")

	// Display final configuration for verification.
	fmt.Printf("\nFinal backup script (%s):\n", targetBackupPath)
	data, err := ioutil.ReadFile(targetBackupPath)
	if err != nil {
		fmt.Printf("Error reading %s: %v\n", targetBackupPath, err)
	} else {
		fmt.Println(string(data))
	}

	fmt.Printf("\nFinal inspect script (%s):\n", targetInspectPath)
	data, err = ioutil.ReadFile(targetInspectPath)
	if err != nil {
		fmt.Printf("Error reading %s: %v\n", targetInspectPath, err)
	} else {
		fmt.Println(string(data))
	}
}
