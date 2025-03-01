package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strings"

	"golang.org/x/term"
)

const (
	CONFIG_FILE         = ".persephone.conf"
	BACKUP_SCRIPT_NAME  = "persephone.bat"
	INSPECT_SCRIPT_NAME = "persephoneInspectSnapshots.bat"
	// Update the target directory as needed.
	TARGET_DIR = `C:\opt\persephone\windows\`
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
			val := strings.TrimSpace(line[idx+1:])
			// Remove surrounding quotes if present.
			val = strings.Trim(val, `"'`)
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
			// Read password without echo.
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

// getConfirmedValue prompts for a value and asks for confirmation.
// If the user does not confirm, it re-prompts.
func getConfirmedValue(key, promptMessage, defaultVal string, hidden bool) string {
	value := promptInput(promptMessage, defaultVal, hidden)
	fmt.Printf("%s is set to: %s\n", key, value)
	confirm := promptInput("Is this correct? (Y/n)", "Y", false)
	lower := strings.ToLower(confirm)
	if lower == "" || lower == "y" || lower == "yes" {
		return value
	}
	// Otherwise, prompt again.
	return promptInput(fmt.Sprintf("Enter new value for %s", key), defaultVal, hidden)
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

// generateBatchScript generates the backup batch script content for Windows.
func generateBatchScript(config map[string]string) string {
	hostname, _ := os.Hostname()
	// Convert comma-separated backup paths into space-separated.
	backupPaths := config["BACKUP_PATHS_STR"]
	backupPaths = strings.ReplaceAll(backupPaths, ",", " ")

	// In a batch file, environment variables are set with "set"
	lines := []string{
		"@echo off",
		"",
		fmt.Sprintf("set AWS_ACCESS_KEY_ID=%s", config["AWS_ACCESS_KEY_ID"]),
		fmt.Sprintf("set AWS_SECRET_ACCESS_KEY=%s", config["AWS_SECRET_ACCESS_KEY"]),
		// Now use the space-separated backupPaths.
		fmt.Sprintf(`restic -r %s --password-file %s backup --verbose %s --tag "%s-%%DATE%-%%TIME%%"`,
			config["PERS_REPO_FILE_VALUE"], config["PERS_PASSWD_FILE"], backupPaths, hostname),
		"echo.",
		"echo Backup complete.",
	}
	return strings.Join(lines, "\r\n")
}

// generateInspectScript generates the inspect snapshots batch script content for Windows.
func generateInspectScript(config map[string]string) string {
	lines := []string{
		"@echo off",
		"",
		fmt.Sprintf("set AWS_ACCESS_KEY_ID=%s", config["AWS_ACCESS_KEY_ID"]),
		fmt.Sprintf("set AWS_SECRET_ACCESS_KEY=%s", config["AWS_SECRET_ACCESS_KEY"]),
		fmt.Sprintf("restic -r %s --password-file %s snapshots", config["PERS_REPO_FILE_VALUE"], config["PERS_PASSWD_FILE"]),
		"echo.",
		"echo Inspection complete.",
	}
	return strings.Join(lines, "\r\n")
}

func main() {
	// Load existing configuration if available.
	config, err := loadConfig(CONFIG_FILE)
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	fmt.Println("=== Restic Backup Configuration ===")

	// --- Repository file and its value ---
	defaultRepoFile := `C:\opt\persephone\windows\persephone-repo.txt`
	if v, ok := config["PERS_REPO_FILE"]; ok {
		defaultRepoFile = v
	}
	persRepoFile := getConfirmedValue("PERS_REPO_FILE", "Enter the repository file path", defaultRepoFile, false)

	defaultRepoValue := "s3:https://persephoneapi.domain.com/repo-name/endpoint-name"
	if v, ok := config["PERS_REPO_FILE_VALUE"]; ok {
		defaultRepoValue = v
	}
	persRepoFileValue := getConfirmedValue("PERS_REPO_FILE_VALUE", "Enter the repository file literal value", defaultRepoValue, false)

	// --- Password file and its value ---
	defaultPassFile := `C:\opt\persephone\windows\persephone-passwd.txt`
	if v, ok := config["PERS_PASSWD_FILE"]; ok {
		defaultPassFile = v
	}
	persPassFile := getConfirmedValue("PERS_PASSWD_FILE", "Enter the password file path", defaultPassFile, false)

	defaultPassValue := "default-password"
	if v, ok := config["PERS_PASSWD_FILE_VALUE"]; ok {
		defaultPassValue = v
	}
	persPassValue := getConfirmedValue("PERS_PASSWD_FILE_VALUE", "Enter the password file literal value", defaultPassValue, true)

	// --- Other configuration values ---
	defaultBackupPaths := `C:\Users,C:\ProgramData,C:\Windows,--exclude "C:\Users\*\AppData\Local\Temp",--exclude "C:\Windows\Temp",--exclude "C:\Windows\WinSxS",--exclude "C:\Users\*\Nextcloud",--exclude "C:\Users\*\OneDrive"`
	if v, ok := config["BACKUP_PATHS_STR"]; ok {
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

	// Generate the backup batch script.
	backupScriptContent := generateBatchScript(config)
	backupScriptPath := filepath.Join(".", BACKUP_SCRIPT_NAME)
	if err := ioutil.WriteFile(backupScriptPath, []byte(backupScriptContent+"\r\n"), 0644); err != nil {
		fmt.Printf("Error writing batch script: %v\n", err)
		return
	}
	fmt.Printf("\nBatch script '%s' generated in current directory.\n", BACKUP_SCRIPT_NAME)

	// Generate the inspect snapshots batch script.
	inspectScriptContent := generateInspectScript(config)
	inspectScriptPath := filepath.Join(".", INSPECT_SCRIPT_NAME)
	if err := ioutil.WriteFile(inspectScriptPath, []byte(inspectScriptContent+"\r\n"), 0644); err != nil {
		fmt.Printf("Error writing inspect script: %v\n", err)
		return
	}
	fmt.Printf("Batch script '%s' generated in current directory.\n", INSPECT_SCRIPT_NAME)

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
	fmt.Printf("Batch scripts moved to: %s\n\n", TARGET_DIR)
	fmt.Printf("Please now run %s to check the backup script works correctly.\n", targetBackupPath)
	fmt.Printf("And run %s to inspect your Persephone snapshots.\n\n", targetInspectPath)
	fmt.Println("If everything works correctly, consider running 'go run createPersephoneSchedule.go' to implement automated regular backups.")
}
