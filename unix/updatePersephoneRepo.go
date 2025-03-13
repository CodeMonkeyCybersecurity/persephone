package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strings"
)

const CONFIG_FILE = ".persephone.conf"
const REPO_FILE = "/root/.persephone-repo"

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

// promptInput reads input from the terminal.
func promptInput(promptMessage string) (string, error) {
	fmt.Print(promptMessage)
	reader := bufio.NewReader(os.Stdin)
	input, err := reader.ReadString('\n')
	if err != nil {
		return "", err
	}
	return strings.TrimSpace(input), nil
}

func main() {
	// Step 1: Read current configuration.
	fmt.Println("Reading configuration from", CONFIG_FILE)
	config, err := loadConfig(CONFIG_FILE)
	if err != nil {
		log.Fatalf("Error loading configuration: %v", err)
	}
	fmt.Println("Configuration loaded.")

	// Step 2: Prompt the user for a new repository URL and confirmation.
	var newRepo, confirmRepo string
	for {
		newRepo, err = promptInput("Enter new repository URL: ")
		if err != nil {
			log.Fatalf("Error reading new repository URL: %v", err)
		}
		confirmRepo, err = promptInput("Confirm new repository URL: ")
		if err != nil {
			log.Fatalf("Error reading repository URL confirmation: %v", err)
		}
		if newRepo != confirmRepo {
			fmt.Println("Repository URLs do not match. Please try again.")
		} else {
			break
		}
	}
	fmt.Println("Repository URL confirmed.")

	// Step 3: Update the repository file (/root/.persephone-repo).
	fmt.Println("Updating repository file at", REPO_FILE)
	err = ioutil.WriteFile(REPO_FILE, []byte(newRepo+"\n"), 0644)
	if err != nil {
		log.Fatalf("Error updating repository file: %v", err)
	}
	fmt.Println("Repository file updated.")

	// Step 4: Update the configuration with the new repository URL.
	config["PERS_REPO_FILE_VALUE"] = newRepo
	err = saveConfig(CONFIG_FILE, config)
	if err != nil {
		log.Fatalf("Error saving configuration: %v", err)
	}
	fmt.Println("Configuration updated with new repository URL.")

	fmt.Println("finis")
}
