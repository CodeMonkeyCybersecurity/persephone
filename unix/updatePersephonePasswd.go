package main

import (
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strings"

	"golang.org/x/term"
)

const CONFIG_FILE = ".persephone.conf"
const PASSWD_FILE = "/root/.persephone-passwd"

// loadConfig loads key-value pairs from the config file.
func loadConfig(configFile string) (map[string]string, error) {
	config := make(map[string]string)
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

// saveConfig writes the config map to the config file.
func saveConfig(configFile string, config map[string]string) error {
	var lines []string
	for key, value := range config {
		lines = append(lines, fmt.Sprintf(`%s="%s"`, key, value))
	}
	data := strings.Join(lines, "\n")
	return ioutil.WriteFile(configFile, []byte(data), 0644)
}

// promptPassword reads a password from the terminal without echoing.
func promptPassword(promptMessage string) (string, error) {
	fmt.Print(promptMessage)
	bytePassword, err := term.ReadPassword(int(os.Stdin.Fd()))
	fmt.Println() // Move to a new line after input.
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(string(bytePassword)), nil
}

func main() {
	// Step 1: Read current configuration.
	fmt.Println("Reading configuration from", CONFIG_FILE)
	config, err := loadConfig(CONFIG_FILE)
	if err != nil {
		log.Fatalf("Error loading configuration: %v", err)
	}
	fmt.Println("Configuration loaded.")

	// Step 2: Prompt the user for a new password and confirmation.
	var newPassword, confirmPassword string
	for {
		newPassword, err = promptPassword("Enter new password: ")
		if err != nil {
			log.Fatalf("Error reading new password: %v", err)
		}
		confirmPassword, err = promptPassword("Confirm new password: ")
		if err != nil {
			log.Fatalf("Error reading password confirmation: %v", err)
		}
		if newPassword != confirmPassword {
			fmt.Println("Passwords do not match. Please try again.")
		} else {
			break
		}
	}
	fmt.Println("Password confirmed.")

	// Step 3: Update the password file (/root/.persephone-passwd).
	fmt.Println("Updating password file at", PASSWD_FILE)
	err = ioutil.WriteFile(PASSWD_FILE, []byte(newPassword+"\n"), 0644)
	if err != nil {
		log.Fatalf("Error updating password file: %v", err)
	}
	fmt.Println("Password file updated.")

	// Step 4: Update the configuration with the new password.
	config["PERS_PASSWD_FILE_VALUE"] = newPassword
	err = saveConfig(CONFIG_FILE, config)
	if err != nil {
		log.Fatalf("Error saving configuration: %v", err)
	}
	fmt.Println("Configuration updated with new password.")

	fmt.Println("finis")
}
