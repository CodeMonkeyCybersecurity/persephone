package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"golang.org/x/term"
)

const CONFIG_FILE = ".persephone.conf"

// loadConfig loads key-value pairs from the config file.
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
			val = strings.Trim(val, `"'`)
			config[key] = val
		}
	}

	return config, nil
}

// Read repository URL from the file (instead of using --repository-file)
func readRepoURL(repoFile string) (string, error) {
    // Check if repoFile exists as a file.
    if _, err := os.Stat(repoFile); err == nil {
        // File exists: read the repository URL from the file.
        content, err := ioutil.ReadFile(repoFile)
        if err != nil {
            return "", fmt.Errorf("error reading repository file: %v", err)
        }
        repoURL := strings.TrimSpace(string(content))
        if repoURL == "" {
            return "", fmt.Errorf("error: repository file %s is empty", repoFile)
        }
        return repoURL, nil
    }
    // File doesn't exist: assume repoFile is the literal repository URL.
    repoURL := repoFile

    // Expand $(hostname) if present.
   	if strings.Contains(repoURL, "$(hostname)") {
		hostname, err := os.Hostname()
		if err != nil {
			return "", fmt.Errorf("error getting hostname: %v", err)
		}
		repoURL = strings.ReplaceAll(repoURL, "$(hostname)", hostname)
	}

    // Debug output:
    fmt.Println("🔍 Using Repo URL:", repoURL)
    return repoURL, nil
}

// saveConfig saves key-value pairs to the config file.
func saveConfig(configFile string, config map[string]string) error {
	var lines []string
	for key, value := range config {
		lines = append(lines, fmt.Sprintf(`%s="%s"`, key, value))
	}
	data := strings.Join(lines, "\n")
	return ioutil.WriteFile(configFile, []byte(data), 0644)
}

// ensureFileExists checks if a file exists, prompts the user for content if missing.
func ensureFileExists(filePath, promptMessage string, hidden bool) error {
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		fmt.Printf("\nFile '%s' not found.\n", filePath)
		// Ensure the parent directory exists.
		absPath, err := filepath.Abs(filePath)
		if err != nil {
			return fmt.Errorf("failed to get absolute path: %w", err)
		}
		parentDir := filepath.Dir(absPath)
		if err := os.MkdirAll(parentDir, 0755); err != nil {
			return fmt.Errorf("failed to create parent directory %s: %w", parentDir, err)
		}

		content := promptInput(promptMessage, "", hidden)
		if err := ioutil.WriteFile(filePath, []byte(strings.TrimSpace(content)+"\n"), 0644); err != nil {
			return err
		}
		fmt.Printf("Created file: %s\n", filePath)
	} else {
		fmt.Printf("Found file: %s\n", filePath)
	}
	return nil
}

// promptInput prompts the user for input, providing a default when available.
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

// main logic
func main() {
	// Load existing configuration
	config, err := loadConfig(CONFIG_FILE)
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	// Retrieve default values from config or set initial defaults.
	defaultRepo := config["PERS_REPO_FILE"]
	if defaultRepo == "" {
		defaultRepo = "/root/.persephone-repo" // Default repo file
	}

	defaultPassFile := config["PERS_PASSWD_FILE"]
	if defaultPassFile == "" {
		defaultPassFile = "/root/.persephone-passwd"
	}

	defaultBackupPaths := config["BACKUP_PATHS_STR"]
	if defaultBackupPaths == "" {
		defaultBackupPaths = "/root /home /var /etc /srv /usr /opt"
	}

	defaultAWSAccessKey := config["AWS_ACCESS_KEY_ID"]
	defaultAWSSecretKey := config["AWS_SECRET_ACCESS_KEY"]

	// Prompt user with defaults retrieved from the config file.
	fmt.Println("=== Restic Backup Configuration ===")
	repoFile := promptInput("Enter the restic repository file path", defaultRepo, false)
	passFile := promptInput("Enter the restic password file path", defaultPassFile, false)
	backupPathsStr := promptInput("Enter backup paths (space-separated)", defaultBackupPaths, false)

	fmt.Println("\n=== AWS Credentials ===")
	awsAccessKey := promptInput("Enter AWS_ACCESS_KEY_ID", defaultAWSAccessKey, false)
	awsSecretKey := promptInput("Enter AWS_SECRET_ACCESS_KEY", defaultAWSSecretKey, true)

	// Read the actual repository URL from file
	repoURL, err := readRepoURL(repoFile)
	if err != nil {
		log.Fatalf("Error reading repository URL: %v", err)
	}

	// Update configuration file with the new values.
	config["PERS_REPO_FILE"] = repoFile
	config["PERS_PASSWD_FILE"] = passFile
	config["BACKUP_PATHS_STR"] = backupPathsStr
	config["AWS_ACCESS_KEY_ID"] = awsAccessKey
	config["AWS_SECRET_ACCESS_KEY"] = awsSecretKey

	if err := saveConfig(CONFIG_FILE, config); err != nil {
		log.Fatalf("Error saving config: %v", err)
	}

	// Ensure the restic password file exists.
	if err := ensureFileExists(passFile, "Enter restic repository password", true); err != nil {
		log.Fatalf("Error ensuring file exists: %v", err)
	}

	// Prepare environment variables for Restic.
	env := os.Environ()
	env = append(env, "AWS_ACCESS_KEY_ID="+awsAccessKey)
	env = append(env, "AWS_SECRET_ACCESS_KEY="+awsSecretKey)

	// Initialize Restic repository if it doesn't exist.
	fmt.Println("Checking if Restic repository is initialized...")
	cmd := exec.Command("sudo", "restic", "-r", repoURL, "--password-file", passFile, "snapshots")
	cmd.Env = env
	if err := cmd.Run(); err != nil {
		fmt.Println("Repository not found or not initialized. Initializing repository...")
		initCmd := exec.Command("sudo", "restic", "-r", repoURL, "--password-file", passFile, "init")
		initCmd.Env = env
		initCmd.Stdout = os.Stdout
		initCmd.Stderr = os.Stderr
		if err := initCmd.Run(); err != nil {
			log.Fatalf("Error initializing repository: %v", err)
		}
		fmt.Println("Repository initialized successfully.")
	} else {
		fmt.Println("Repository is already initialized.")
	}

	// Run the backup.
	runBackup := promptInput("\nDo you want to run the backup now? (y/n)", "y", false)
	if strings.ToLower(runBackup) == "y" {
		backupCmd := exec.Command("sudo", "restic", "-r", repoURL, "--password-file", passFile, "backup")
		backupCmd.Args = append(backupCmd.Args, strings.Fields(backupPathsStr)...)

		fmt.Println("\nRunning Restic backup...")
		backupCmd.Env = env
		backupCmd.Stdout = os.Stdout
		backupCmd.Stderr = os.Stderr
		if err := backupCmd.Run(); err != nil {
			log.Fatalf("Error during backup: %v", err)
		}
		fmt.Println("Backup completed successfully.")
	} else {
		fmt.Println("Backup not executed.")
	}
}
