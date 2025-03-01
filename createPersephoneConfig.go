package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"path/filepath"
	"strings"
	"time"

	"golang.org/x/term"
)

const CONFIG_FILE = ".persephone.conf"

// loadConfig loads configuration from a file (one key="value" per line)
// and returns a map of the configuration values.
func loadConfig(configFile string) (map[string]string, error) {
	config := make(map[string]string)
	if _, err := os.Stat(configFile); err == nil {
		data, err := ioutil.ReadFile(configFile)
		if err != nil {
			return config, err
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
				val = strings.Trim(val, `"'`)
				config[key] = val
			}
		}
	}
	return config, nil
}

// backupExistingConfig makes a backup of an existing configuration file.
func backupExistingConfig(configFile string) {
	if _, err := os.Stat(configFile); err == nil {
		timestamp := time.Now().Format("20060102_150405")
		backupFile := fmt.Sprintf("%s.%s.bak", configFile, timestamp)
		input, err := ioutil.ReadFile(configFile)
		if err != nil {
			fmt.Printf("Error reading config for backup: %v\n", err)
			return
		}
		if err := ioutil.WriteFile(backupFile, input, 0644); err != nil {
			fmt.Printf("Error writing backup file: %v\n", err)
		} else {
			fmt.Printf("Existing config found. Backed up to: %s\n", backupFile)
		}
	}
}

// promptInput prompts the user for input with an optional default value.
// If hidden is true, the input is not echoed.
func promptInput(promptMessage, defaultVal string, hidden bool) string {
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
			reader := bufio.NewReader(os.Stdin)
			input, err := reader.ReadString('\n')
			if err != nil {
				log.Printf("Error reading input: %v", err)
				continue
			}
			input = strings.TrimSpace(input)
			if input == "" && defaultVal != "" {
				return defaultVal
			} else if input != "" {
				return input
			}
		}
		fmt.Println("Error: Input cannot be empty. Please enter a valid value.")
	}
}

// promptConfirmedPassword prompts the user to enter a password twice for confirmation.
func promptConfirmedPassword(promptMessage string) string {
	for {
		fmt.Print(promptMessage + ": ")
		p1Bytes, err := term.ReadPassword(int(os.Stdin.Fd()))
		fmt.Println()
		if err != nil {
			log.Printf("Error reading password: %v", err)
			continue
		}
		p1 := strings.TrimSpace(string(p1Bytes))
		fmt.Print("Confirm " + promptMessage + ": ")
		p2Bytes, err := term.ReadPassword(int(os.Stdin.Fd()))
		fmt.Println()
		if err != nil {
			log.Printf("Error reading confirmation: %v", err)
			continue
		}
		p2 := strings.TrimSpace(string(p2Bytes))
		if p1 == p2 {
			return p1
		} else {
			fmt.Println("Passwords do not match. Please try again.")
		}
	}
}

// getConfirmedValue prompts for a value with a default, shows the current setting,
// and asks for confirmation. If not confirmed, it prompts for a new value.
func getConfirmedValue(key, promptMessage, defaultVal string) string {
	value := promptInput(promptMessage, defaultVal, false)
	fmt.Printf("%s is set to: %s\n", key, value)
	confirm := promptInput("Is this correct? (Y/n)", "Y", false)
	if strings.EqualFold(confirm, "y") || confirm == "" || strings.EqualFold(confirm, "yes") {
		return value
	}
	return promptInput(fmt.Sprintf("Enter new value for %s", key), defaultVal, false)
}

// getConfirmedFileValue checks a file's content. If the file exists, it reads and displays its content,
// then asks the user to confirm that the literal value is correct.
// If not, it prompts for a new value and overwrites the file.
// If the file doesn't exist, it prompts for a value and creates the file.
func getConfirmedFileValue(filePath, description string, hidden bool) string {
	if _, err := os.Stat(filePath); err == nil {
		data, err := ioutil.ReadFile(filePath)
		currentValue := ""
		if err != nil {
			fmt.Printf("Error reading %s file at %s: %v\n", description, filePath, err)
		} else {
			currentValue = strings.TrimSpace(string(data))
		}
		fmt.Printf("%s file found at '%s' with content:\n  %s\n", description, filePath, currentValue)
		confirm := promptInput(fmt.Sprintf("Is this the correct value for %s? (Y/n)", description), "Y", false)
		if strings.EqualFold(confirm, "y") || confirm == "" || strings.EqualFold(confirm, "yes") {
			return currentValue
		}
		newValue := promptInput(fmt.Sprintf("Enter new literal value for %s", description), currentValue, hidden)
		if err := ioutil.WriteFile(filePath, []byte(newValue+"\n"), 0644); err != nil {
			fmt.Printf("Error updating %s file at %s: %v\n", description, filePath, err)
		} else {
			fmt.Printf("Updated %s file at %s.\n", description, filePath)
		}
		return newValue
	} else {
		fmt.Printf("%s file does not exist at %s. It will be created.\n", description, filePath)
		newValue := promptInput(fmt.Sprintf("Enter literal value for %s", description), "", hidden)
		// Ensure the parent directory exists.
		parentDir := filepath.Dir(filePath)
		if parentDir != "" {
			os.MkdirAll(parentDir, 0755)
		}
		if err := ioutil.WriteFile(filePath, []byte(newValue+"\n"), 0644); err != nil {
			fmt.Printf("Error creating %s file at %s: %v\n", description, filePath, err)
		} else {
			fmt.Printf("Created %s file at %s with provided value.\n", description, filePath)
		}
		return newValue
	}
}

// getConfirmedPasswordFileValue performs a similar function as getConfirmedFileValue
// but is specialized for password files. It asks whether the current password is correct.
// If not, it prompts for a new password (confirmed twice).
func getConfirmedPasswordFileValue(filePath, description string) string {
	if _, err := os.Stat(filePath); err == nil {
		data, err := ioutil.ReadFile(filePath)
		currentValue := ""
		if err != nil {
			fmt.Printf("Error reading %s file at %s: %v\n", description, filePath, err)
		} else {
			currentValue = strings.TrimSpace(string(data))
		}
		fmt.Printf("%s file found at '%s'.\n", description, filePath)
		confirm := promptInput("Is the current password correct? (Y/n)", "Y", false)
		if strings.EqualFold(confirm, "y") || confirm == "" || strings.EqualFold(confirm, "yes") {
			return currentValue
		}
		newValue := promptConfirmedPassword(fmt.Sprintf("Enter new password for %s", description))
		if err := ioutil.WriteFile(filePath, []byte(newValue+"\n"), 0644); err != nil {
			fmt.Printf("Error updating %s file at %s: %v\n", description, filePath, err)
		} else {
			fmt.Printf("Updated %s file at %s.\n", description, filePath)
		}
		return newValue
	} else {
		fmt.Printf("%s file does not exist at %s. It will be created.\n", description, filePath)
		newValue := promptConfirmedPassword(fmt.Sprintf("Enter password for %s", description))
		parentDir := filepath.Dir(filePath)
		if parentDir != "" {
			os.MkdirAll(parentDir, 0755)
		}
		if err := ioutil.WriteFile(filePath, []byte(newValue+"\n"), 0644); err != nil {
			fmt.Printf("Error creating %s file at %s: %v\n", description, filePath, err)
		} else {
			fmt.Printf("Created %s file at %s with provided value.\n", description, filePath)
		}
		return newValue
	}
}

func main() {
	// Load any existing configuration.
	existingConfig, err := loadConfig(CONFIG_FILE)
	if err != nil {
		log.Printf("Error loading existing configuration: %v\n", err)
	}

	// --- For the repository file and its value ---
	defaultRepoFile := "/root/.persephone-repo"
	if val, ok := existingConfig["PERS_REPO_FILE"]; ok {
		defaultRepoFile = val
	}
	persRepoFile := getConfirmedValue("PERS_REPO_FILE", "Enter the repository file path", defaultRepoFile)
	persRepoFileValue := getConfirmedFileValue(persRepoFile, "PERS_REPO_FILE_VALUE", false)

	// --- For the password file and its value ---
	defaultPasswdFile := "/root/.persephone-passwd"
	if val, ok := existingConfig["PERS_PASSWD_FILE"]; ok {
		defaultPasswdFile = val
	}
	persPasswdFile := getConfirmedValue("PERS_PASSWD_FILE", "Enter the password file path", defaultPasswdFile)
	persPasswdFileValue := getConfirmedPasswordFileValue(persPasswdFile, "PERS_PASSWD_FILE_VALUE")

	// --- Other configuration values ---
	backupPathsStr := ""
	if val, ok := existingConfig["BACKUP_PATHS_STR"]; ok {
		backupPathsStr = val
	} else {
		backupPathsStr = promptInput("Enter backup paths (space-separated)", "/root /home /var /etc /srv /usr /opt", false)
	}
	awsAccessKey := ""
	if val, ok := existingConfig["AWS_ACCESS_KEY_ID"]; ok {
		awsAccessKey = val
	} else {
		awsAccessKey = promptInput("Enter AWS_ACCESS_KEY_ID", "", false)
	}
	awsSecretKey := ""
	if val, ok := existingConfig["AWS_SECRET_ACCESS_KEY"]; ok {
		awsSecretKey = val
	} else {
		awsSecretKey = promptInput("Enter AWS_SECRET_ACCESS_KEY", "", true)
	}

	// Back up existing configuration file.
	backupExistingConfig(CONFIG_FILE)

	// Prepare the new configuration.
	config := map[string]string{
		"PERS_REPO_FILE":         persRepoFile,
		"PERS_REPO_FILE_VALUE":   persRepoFileValue,
		"PERS_PASSWD_FILE":       persPasswdFile,
		"PERS_PASSWD_FILE_VALUE": persPasswdFileValue,
		"BACKUP_PATHS_STR":       backupPathsStr,
		"AWS_ACCESS_KEY_ID":      awsAccessKey,
		"AWS_SECRET_ACCESS_KEY":  awsSecretKey,
	}

	// Write the new configuration to the config file.
	f, err := os.Create(CONFIG_FILE)
	if err != nil {
		fmt.Printf("Error saving configuration: %v\n", err)
		return
	}
	defer f.Close()
	writer := bufio.NewWriter(f)
	for key, value := range config {
		_, err := writer.WriteString(fmt.Sprintf(`%s="%s"`+"\n", key, value))
		if err != nil {
			fmt.Printf("Error writing configuration for %s: %v\n", key, err)
		}
	}
	writer.Flush()
	fmt.Printf("\nConfiguration successfully saved to %s.\n\n", CONFIG_FILE)
	fmt.Println("please now run ./createPersephoneBackupS3Script.py to create the backup script.\n")
}
