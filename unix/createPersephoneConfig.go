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

//
// loadConfig loads a key="value" file into a map.
//
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

//
// backupExistingConfig creates a backup of the config file if it exists.
//
func backupExistingConfig(configFile string) {
	if _, err := os.Stat(configFile); err == nil {
		backupFile := fmt.Sprintf("%s.%s.bak", configFile, time.Now().Format("20060102_150405"))
		if err := os.Rename(configFile, backupFile); err == nil {
			fmt.Printf("Backup created: %s\n", backupFile)
		}
	}
}

//
// getInput prompts the user for input.
// If 'hidden' is true the input will not be echoed.
// If 'confirm' is true, the user is asked to confirm the input.
//
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
		confirmInput := getInput("Confirm: ", "", hidden, false)
		if confirmInput == input {
			return input
		}
		fmt.Println("Inputs do not match. Try again.")
	}
}

//
// getConfirmedFileValue ensures that a file exists with the proper content.
// If the file exists, its content is shown and the user is asked if it is correct.
// If not, the user is prompted to enter a new value which is then written to the file.
//
func getConfirmedFileValue(filePath, description string, isPassword bool) string {
	if data, err := os.ReadFile(filePath); err == nil {
		currentValue := strings.TrimSpace(string(data))
		fmt.Printf("%s file found at '%s' with content:\n  %s\n", description, filePath, currentValue)
		confirm := getInput(fmt.Sprintf("Is this the correct value for %s? (Y/n): ", description), "Y", false, false)
		if strings.EqualFold(confirm, "y") || confirm == "" || strings.EqualFold(confirm, "yes") {
			return currentValue
		}
		fmt.Printf("Updating %s file...\n", description)
	} else {
		fmt.Printf("%s file not found at %s. It will be created.\n", description, filePath)
	}
	newValue := getInput(fmt.Sprintf("Enter new literal value for %s: ", description), "", isPassword, isPassword)
	os.MkdirAll(filepath.Dir(filePath), 0755)
	if err := os.WriteFile(filePath, []byte(newValue+"\n"), 0644); err != nil {
		fmt.Printf("Error updating %s file at %s: %v\n", description, filePath, err)
	} else {
		fmt.Printf("Updated %s file at %s.\n", description, filePath)
	}
	return newValue
}

//
// main runs the configuration process.
//
func main() {
	existingConfig := loadConfig(CONFIG_FILE)
	backupExistingConfig(CONFIG_FILE)

	// Define a configuration map for most settings.
	configPrompts := map[string]struct {
		Prompt  string
		Default string
		Hidden  bool
		Confirm bool
		IsFile  bool
	}{
		"PERS_REPO_FILE":         {"Enter the repository file path", "/root/.persephone-repo", false, false, false},
		"BACKUP_PATHS_STR":       {"Enter backup paths (space-separated)", "/root /home /var /etc /srv /usr /opt", false, false, false},
		"AWS_ACCESS_KEY_ID":      {"Enter AWS Access Key", "", false, false, false},
		"AWS_SECRET_ACCESS_KEY":  {"Enter AWS Secret Key", "", true, true, false},
		"PERS_REPO_FILE_VALUE":   {"Confirm repository file contents", "", false, false, true},
		"PERS_PASSWD_FILE_VALUE": {"Confirm password file contents", "", true, true, true},
	}

	config := make(map[string]string)

	// Special handling for the password file path.
	{
		const defaultPasswdFile = "/root/.persephone-passwd"
		var defaultVal string
		if val, ok := existingConfig["PERS_PASSWD_FILE"]; ok && val != "" {
			defaultVal = val
		} else {
			defaultVal = defaultPasswdFile
		}
		// Ask the user if they want to use the default/existing value.
		confirmPrompt := fmt.Sprintf("Do you want to use the %s password file path (%s) [Y/n]: ",
			func() string {
				if _, ok := existingConfig["PERS_PASSWD_FILE"]; ok {
					return "existing"
				}
				return "default"
			}(),
			defaultVal)
		confirm := getInput(confirmPrompt, "Y", false, false)
		if strings.EqualFold(confirm, "y") || confirm == "" || strings.EqualFold(confirm, "yes") {
			config["PERS_PASSWD_FILE"] = defaultVal
		} else {
			config["PERS_PASSWD_FILE"] = getInput("Enter new password file path: ", defaultVal, false, false)
		}
	}

	// Process other configuration values.
	for key, info := range configPrompts {
		var value string
		// For file values, use the specialized function.
		if info.IsFile {
			// Use the pre-existing value if found.
			defaultVal := existingConfig[key]
			if defaultVal == "" {
				defaultVal = ""
			}
			value = getConfirmedFileValue(defaultVal, info.Prompt, info.Hidden)
		} else {
			defaultVal := existingConfig[key]
			value = getInput(info.Prompt+": ", defaultVal, info.Hidden, info.Confirm)
		}
		config[key] = value
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
