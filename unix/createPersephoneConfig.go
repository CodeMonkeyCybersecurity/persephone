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
func getConfirmedFileValue(filePath, prompt string, isPassword bool) string {
	// Attempt to read the file
	if data, err := os.ReadFile(filePath); err == nil {
		currentValue := strings.TrimSpace(string(data))
		// Print the prompt and the current file content
		fmt.Printf("%s\n  %s\n", prompt, currentValue)
		confirm := getInput("Your answer: ", "Y", false, false)
		if strings.EqualFold(confirm, "y") || confirm == "" || strings.EqualFold(confirm, "yes") {
			return currentValue
		}
		fmt.Printf("Updating file at %s...\n", filePath)
	} else {
		fmt.Printf("File not found at %s. It will be created.\n", filePath)
	}
	// Prompt for new value if needed
	newValue := getInput("Enter new value: ", "", isPassword, isPassword)
	os.MkdirAll(filepath.Dir(filePath), 0755)
	if err := os.WriteFile(filePath, []byte(newValue+"\n"), 0644); err != nil {
		fmt.Printf("Error updating file at %s: %v\n", filePath, err)
	} else {
		fmt.Printf("Updated file at %s.\n", filePath)
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
		// These keys are handled separately so they're removed from this map:
		// "PERS_REPO_FILE",
		// "BACKUP_PATHS_STR",
		// "PERS_PASSWD_FILE",
		"AWS_ACCESS_KEY_ID":     {"Enter AWS Access Key", "", false, false, false},
		"AWS_SECRET_ACCESS_KEY": {"Enter AWS Secret Key", "", true, true, false},
		"PERS_REPO_FILE_VALUE":  {"Please make sure this is the correct address for your Persephone repository (Y/n):", "", false, false, true},
		"PERS_PASSWD_FILE_VALUE": {"Please confirm your Persephone repository password (Y/n):", "", true, true, true},
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
	
	{
		const defaultBackupPaths = "/root /home /var /etc /srv /usr /opt"
		var defaultVal string
		if val, ok := existingConfig["BACKUP_PATHS_STR"]; ok && val != "" {
			defaultVal = val
		} else {
			defaultVal = defaultBackupPaths
		}
		confirmPrompt := fmt.Sprintf("Do you want to use the %s backup paths (%s) [Y/n]: ",
			func() string {
				if _, ok := existingConfig["BACKUP_PATHS_STR"]; ok {
					return "existing"
				}
				return "default"
			}(),
			defaultVal)
		confirm := getInput(confirmPrompt, "Y", false, false)
		if strings.EqualFold(confirm, "y") || confirm == "" || strings.EqualFold(confirm, "yes") {
			config["BACKUP_PATHS_STR"] = defaultVal
		} else {
			config["BACKUP_PATHS_STR"] = getInput("Enter new backup paths (space-separated): ", defaultVal, false, false)
		}
	}
	{
		const defaultRepoFile = "/root/.persephone-repo"
		var defaultVal string
		if val, ok := existingConfig["PERS_REPO_FILE"]; ok && val != "" {
			defaultVal = val
		} else {
			defaultVal = defaultRepoFile
		}
		confirmPrompt := fmt.Sprintf("Do you want to use the %s repository file path (%s) [Y/n]: ",
			func() string {
				if _, ok := existingConfig["PERS_REPO_FILE"]; ok {
					return "existing"
				}
				return "default"
			}(),
			defaultVal)
		confirm := getInput(confirmPrompt, "Y", false, false)
		if strings.EqualFold(confirm, "y") || confirm == "" || strings.EqualFold(confirm, "yes") {
			config["PERS_REPO_FILE"] = defaultVal
		} else {
			config["PERS_REPO_FILE"] = getInput("Enter new repository file path: ", defaultVal, false, false)
		}
	}
	// Process other configuration values.
	for key, info := range configPrompts {
	    var value string
	    if info.IsFile {
	        // For file content keys, determine the proper file path.
	        var filePath string
	        switch key {
	        case "PERS_REPO_FILE_VALUE":
	            filePath = config["PERS_REPO_FILE"]  // use the confirmed repository file path
	        case "PERS_PASSWD_FILE_VALUE":
	            filePath = config["PERS_PASSWD_FILE"]  // use the confirmed password file path
	        default:
	            filePath = existingConfig[key]  // fallback, if any
	        }
	        value = getConfirmedFileValue(filePath, info.Prompt, info.Hidden)
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
