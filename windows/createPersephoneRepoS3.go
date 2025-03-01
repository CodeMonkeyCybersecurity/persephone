package main

import (
	"bufio"
	"bytes"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"os/exec"
	"path/filepath"
	"strings"

	"golang.org/x/term"
)

const (
	CONFIG_FILE = ".persephone_backup.conf"
)

// loadConfig reads a config file (key="value" per line) and returns a map.
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
			// Remove surrounding quotes.
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

// saveConfig writes the config map to a file.
func saveConfig(configFile string, config map[string]string) error {
	var lines []string
	for key, value := range config {
		lines = append(lines, fmt.Sprintf(`%s="%s"`, key, value))
	}
	data := strings.Join(lines, "\n")
	return ioutil.WriteFile(configFile, []byte(data), 0644)
}

// repoInitialized checks if the restic repository is initialized by listing snapshots.
func repoInitialized(repoFile, passFile string, env []string) bool {
	// On Windows, no need for "sudo"
	cmd := exec.Command("restic",
		"--repository-file", repoFile,
		"--password-file", passFile,
		"snapshots",
	)
	cmd.Env = env

	var stderr bytes.Buffer
	cmd.Stderr = &stderr

	if err := cmd.Run(); err != nil {
		errMsg := stderr.String()
		if strings.Contains(errMsg, "does not exist") || strings.Contains(errMsg, "open repository") {
			return false
		}
		return false
	}
	return true
}

// initializeRepo runs the restic init command to initialize the repository.
func initializeRepo(repoFile, passFile string, env []string) error {
	fmt.Println("Repository not found or not initialized. Initializing repository...")
	cmd := exec.Command("restic",
		"--repository-file", repoFile,
		"--password-file", passFile,
		"init",
	)
	cmd.Env = env
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	if err := cmd.Run(); err != nil {
		return err
	}
	fmt.Println("Repository initialized successfully.")
	return nil
}

// ensureFileExists checks if a file exists; if not, prompts for content and creates it.
func ensureFileExists(filePath, promptMessage string, hidden bool) error {
	if _, err := os.Stat(filePath); os.IsNotExist(err) {
		fmt.Printf("\nFile '%s' not found.\n", filePath)
		// Ensure parent directory exists.
		parentDir := filepath.Dir(filePath)
		if parentDir != "" {
			os.MkdirAll(parentDir, 0755)
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

func main() {
	// Load configuration if available.
	config, err := loadConfig(CONFIG_FILE)
	if err != nil {
		log.Fatalf("Error loading config: %v", err)
	}

	// Set default values (or use values from config).
	// Update defaults to Windows-style paths.
	defaultRepo := "s3:https://s3api.cybermonkey.dev/restic"
	if v, ok := config["REPO_FILE"]; ok {
		defaultRepo = v
	}
	defaultPassFile := `C:\Persephone\.restic-password`
	if v, ok := config["PASS_FILE"]; ok {
		defaultPassFile = v
	}
	defaultBackupPaths := `C:\Users C:\ProgramData`
	if v, ok := config["BACKUP_PATHS_STR"]; ok {
		defaultBackupPaths = v
	}
	defaultAWSAccessKey := ""
	if v, ok := config["AWS_ACCESS_KEY_ID"]; ok {
		defaultAWSAccessKey = v
	}
	defaultAWSSecretKey := ""
	if v, ok := config["AWS_SECRET_ACCESS_KEY"]; ok {
		defaultAWSSecretKey = v
	}

	fmt.Println("=== Restic Backup Configuration ===")
	repoFile := promptInput("Enter the restic repository file path", defaultRepo, false)
	passFile := promptInput("Enter the restic password file path", defaultPassFile, false)
	backupPathsStr := promptInput("Enter backup paths (space-separated)", defaultBackupPaths, false)

	fmt.Println("\n=== AWS Credentials ===")
	awsAccessKey := promptInput("Enter AWS_ACCESS_KEY_ID", defaultAWSAccessKey, false)
	awsSecretKey := promptInput("Enter AWS_SECRET_ACCESS_KEY", defaultAWSSecretKey, true)

	// Update configuration map.
	config["REPO_FILE"] = repoFile
	config["PASS_FILE"] = passFile
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

	// Prepare environment variables.
	env := os.Environ()
	env = append(env, "AWS_ACCESS_KEY_ID="+awsAccessKey)
	env = append(env, "AWS_SECRET_ACCESS_KEY="+awsSecretKey)

	// Check if repository is initialized.
	if !repoInitialized(repoFile, passFile, env) {
		if err := initializeRepo(repoFile, passFile, env); err != nil {
			log.Fatalf("Error initializing repository: %v", err)
		}
	} else {
		fmt.Println("Repository is already initialized.")
	}

	// Prompt user to run backup.
	runBackup := promptInput("\nDo you want to run the backup now? (y/n)", "y", false)
	if strings.HasPrefix(strings.ToLower(runBackup), "y") {
		backupPaths := strings.Fields(backupPathsStr)
		backupCmd := []string{
			"restic",
			"--repository-file", repoFile,
			"--password-file", passFile,
			"--verbose", "backup",
		}
		backupCmd = append(backupCmd, backupPaths...)
		fmt.Println("\nRunning Restic backup...")
		cmd := exec.Command(backupCmd[0], backupCmd[1:]...)
		cmd.Env = env
		cmd.Stdout = os.Stdout
		cmd.Stderr = os.Stderr
		if err := cmd.Run(); err != nil {
			log.Fatalf("Error during backup: %v", err)
		}

		// Check snapshots.
		fmt.Println("Backup completed. Checking snapshots...")
		snapshotsCmd := exec.Command("restic",
			"--repository-file", repoFile,
			"--password-file", passFile,
			"snapshots",
		)
		snapshotsCmd.Env = env
		snapshotsCmd.Stdout = os.Stdout
		snapshotsCmd.Stderr = os.Stderr
		if err := snapshotsCmd.Run(); err != nil {
			log.Fatalf("Error checking snapshots: %v", err)
		}

		fmt.Println("Restic backup and snapshot check complete.")
	} else {
		fmt.Println("Backup not executed.")
	}
}
