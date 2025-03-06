package main

import (
	"bufio"
	"fmt"
	"os"
	"os/exec"
	"strings"
)

// Configuration file path
const configFilePath = ".persephone.conf"

// Read the configuration file and return a map of key-value pairs
func readConfig() (map[string]string, error) {
	config := make(map[string]string)

	file, err := os.Open(configFilePath)
	if err != nil {
		return nil, err
	}
	defer file.Close()

	scanner := bufio.NewScanner(file)
	for scanner.Scan() {
		line := strings.TrimSpace(scanner.Text())
		if line == "" || strings.HasPrefix(line, "#") {
			continue
		}
		parts := strings.SplitN(line, "=", 2)
		if len(parts) != 2 {
			continue
		}
		key := strings.TrimSpace(parts[0])
		value := strings.Trim(strings.TrimSpace(parts[1]), "\"") // Remove surrounding quotes
		config[key] = value
	}

	return config, scanner.Err()
}

// Validate credentials by running a Restic command
func validateCredentials(config map[string]string) bool {
	repo := config["PERS_REPO_FILE_VALUE"]
	password := config["PERS_PASSWD_FILE_VALUE"]
	accessKey := config["AWS_ACCESS_KEY_ID"]
	secretKey := config["AWS_SECRET_ACCESS_KEY"]

	if repo == "" || password == "" {
		fmt.Println("Error: Missing repository URL or password.")
		return false
	}

	// Prepare environment variables for Restic
	env := os.Environ()
	env = append(env, "RESTIC_REPOSITORY="+repo, "RESTIC_PASSWORD="+password)

	// If it's an S3 repository, add AWS credentials
	if strings.HasPrefix(repo, "s3:") {
		if accessKey == "" || secretKey == "" {
			fmt.Println("Error: S3 repository detected, but AWS credentials are missing.")
			return false
		}
		env = append(env, "AWS_ACCESS_KEY_ID="+accessKey, "AWS_SECRET_ACCESS_KEY="+secretKey)
	}

	// Run Restic command to check credentials
	cmd := exec.Command("restic", "snapshots")
	cmd.Env = env
	output, err := cmd.CombinedOutput()

	if err != nil {
		fmt.Println("Restic authentication failed!")
		fmt.Println("Error:", err)
		fmt.Println("Output:", string(output))
		return false
	}

	fmt.Println("✅ Credentials are valid. Restic repository is accessible.")
	fmt.Println("Restic Output:\n", string(output))
	return true
}

func main() {
	fmt.Println("Checking Persephone credentials...")

	// Read config file
	config, err := readConfig()
	if err != nil {
		fmt.Println("Error reading config file:", err)
		os.Exit(1)
	}

	// Validate credentials
	if !validateCredentials(config) {
		os.Exit(1) // Exit with failure
	}
}
