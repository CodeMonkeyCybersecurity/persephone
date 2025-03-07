package main

import (
	"bufio"
	"fmt"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"golang.org/x/term"
)

const CONFIG_FILE = ".persephone.conf"

// Reads a key-value formatted config file into a map.
func loadConfig(configFile string) map[string]string {
	config := make(map[string]string)
	data, err := os.ReadFile(configFile)
	if err != nil {
		return config
	}
	for _, line := range strings.Split(string(data), "\n") {
		line = strings.TrimSpace(line)
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) == 2 {
			config[strings.TrimSpace(parts[0])] = strings.Trim(strings.TrimSpace(parts[1]), `"'`)
		}
	}
	return config
}

// Creates a timestamped backup of an existing configuration file.
func backupExistingConfig(configFile string) {
	if _, err := os.Stat(configFile); err == nil {
		backupFile := fmt.Sprintf("%s.%s.bak", configFile, time.Now().Format("20060102_150405"))
		if err := os.Rename(configFile, backupFile); err == nil {
			fmt.Printf("Backup created: %s\n", backupFile)
		}
	}
}

// Generalized function to get user input with optional password masking and confirmation.
func getInput(prompt, defaultVal string, hidden, confirm bool) string {
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
			reader := bufio.NewReader(os.Stdin)
			rawInput, _ := reader.ReadString('\n')
			input = strings.TrimSpace(rawInput)
		}
		if input == "" {
			input = defaultVal
		}
		if !confirm {
			return input
		}
		fmt.Print("Confirm: ")
		if confirmInput := getInput("", "", hidden, false); confirmInput == input {
			return input
		}
		fmt.Println("Inputs do not match. Try again.")
	}
}

// Ensures a configuration file exists with a valid value.
func getConfirmedFileValue(filePath, description string, isPassword bool) string {
	if data, err := os.ReadFile(filePath); err == nil {
		currentValue := strings.TrimSpace(string(data))
		fmt.Printf("%s found at '%s' with content:\n  %s\n", description, filePath, currentValue)
		if getInput("Is this correct? (Y/n): ", "Y", false, false) == "Y" {
			return currentValue
		}
	}
	newValue := getInput(fmt.Sprintf("Enter value for %s: ", description), "", isPassword, isPassword)
	os.MkdirAll(filepath.Dir(filePath), 0755)
	os.WriteFile(filePath, []byte(newValue+"\n"), 0644)
	fmt.Printf("Updated %s at %s\n", description, filePath)
	return newValue
}

func main() {
	existingConfig := loadConfig(CONFIG_FILE)
	backupExistingConfig(CONFIG_FILE)

	// Define configuration prompts
	configPrompts := map[string]struct {
		Prompt    string
		Default   string
		Hidden    bool
		Confirm   bool
		IsFile    bool
	}{
		"PERS_REPO_FILE":         {"Enter the repository file path", "/root/.persephone-repo", false, false, false},
		"PERS_PASSWD_FILE":       {"Enter the password file path", "/root/.persephone-passwd", false, false, false},
		"BACKUP_PATHS_STR":       {"Enter backup paths (space-separated)", "/root /home /var /etc /srv /usr /opt", false, false, false},
		"AWS_ACCESS_KEY_ID":      {"Enter AWS Access Key", "", false, false, false},
		"AWS_SECRET_ACCESS_KEY":  {"Enter AWS Secret Key", "", true, true, false},
		"PERS_REPO_FILE_VALUE":   {"Confirm repository file contents", "", false, false, true},
		"PERS_PASSWD_FILE_VALUE": {"Confirm password file contents", "", true, true, true},
	}

	config := make(map[string]string)
	for key, info := range configPrompts {
		defaultVal := existingConfig[key]
		if info.IsFile {
			config[key] = getConfirmedFileValue(defaultVal, info.Prompt, info.Hidden)
		} else {
			config[key] = getInput(info.Prompt+": ", defaultVal, info.Hidden, info.Confirm)
		}
	}

	// Write the new configuration to the config file.
	f, err := os.Create(CONFIG_FILE)
	if err != nil {
		log.Fatalf("Error saving configuration: %v", err)
	}
	defer f.Close()
	writer := bufio.NewWriter(f)
	for key, value := range config {
		writer.WriteString(fmt.Sprintf(`%s="%s"`+"\n", key, value))
	}
	writer.Flush()

	fmt.Printf("\nConfiguration saved to %s.\n", CONFIG_FILE)
	fmt.Println("Next steps:")
	fmt.Println("- Run 'go run createPersephoneRepoS3.go' to initialize the repository.")
	fmt.Println("- Run 'go run createPersephoneBackupS3Script.go' to create the backup script.")
}
