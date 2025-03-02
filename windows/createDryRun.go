package main

import (
	"fmt"
	"log"
	"os/exec"
)

const (
	CONFIG_FILE         = ".persephone.conf"
	TARGET_DIR = `C:/opt/persephone/windows/`
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

func main() {
	// Set these values as appropriate for your environment.
	// Use forward slashes in paths for consistency.
	repo := "s3:https://persephoneapi.cybermonkey.dev/restic/H-Windows"
	passFile := `C:/opt/persephone/windows/persephone-passwd.txt`
	// List the backup paths along with exclude flags as separate arguments.
	// Note: Adjust the paths/exclusions to match what you want to exclude.
	args := []string{
		"--repo", repo,
		"--password-file", passFile,
		"backup",
		"--dry-run",
		"C:/Users",
		"C:/ProgramData",
		"C:/Windows",
		"--exclude", "C:/Users/*/AppData/Local/Temp",
		"--exclude", "C:/Windows/Temp",
		"--exclude", "C:/Windows/WinSxS",
		"--exclude", "C:/Users/*/Nextcloud",
		"--exclude", "C:/Users/*/OneDrive",
	}

	// Execute the restic backup command in dry-run mode.
	cmd := exec.Command("restic", args...)
	output, err := cmd.CombinedOutput()
	if err != nil {
		log.Fatalf("Dry-run backup failed: %v\nOutput:\n%s", err, string(output))
	}

	fmt.Println("Dry-run backup output:")
	fmt.Println(string(output))
}
