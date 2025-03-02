package main

import (
	"bufio"
	"fmt"
	"io/ioutil"
	"log"
	"os"
	"strings"
	"time"

	"golang.org/x/term"
)

// Update these constants with the desired Windows file paths.
const (
	REPO_PATH   = "C:/opt/persephone/windows/persephone-repo.txt"
	PASSWD_PATH = "C:/opt/persephone/windows/persephone-passwd.txt"
)

// checkAndUpdateFile checks if a file exists and if its content is correct.
// If not, it prompts the user for new content (hidden input if needed), writes it to the file,
// and returns the final content.
func checkAndUpdateFile(path, description string, hidden bool) string {
	var currentContent string

	// Check if file exists.
	_, err := os.Stat(path)
	if err == nil {
		// File exists; read its contents.
		data, err := ioutil.ReadFile(path)
		if err != nil {
			fmt.Printf("Error reading %s file at %s: %v\n", description, path, err)
		} else {
			currentContent = strings.TrimSpace(string(data))
		}
		fmt.Printf("%s file found at %s.\n", description, path)
		fmt.Printf("Current contents: %s\n", currentContent)

		// Prompt for confirmation.
		fmt.Print("Is this correct? (Y/n): ")
		reader := bufio.NewReader(os.Stdin)
		resp, _ := reader.ReadString('\n')
		resp = strings.TrimSpace(strings.ToLower(resp))
		if resp == "" || resp == "y" || resp == "yes" {
			fmt.Printf("No update needed for %s file.\n", description)
			return currentContent
		}
		fmt.Printf("Updating %s file...\n", description)
	} else {
		fmt.Printf("%s file not found at %s. It will be created.\n", description, path)
		// Ensure the parent directory exists.
		if err := os.MkdirAll(getDir(path), 0755); err != nil {
			log.Fatalf("Failed to create directory for %s: %v\n", path, err)
		}
	}

	// Prompt for new content.
	var newContent string
	if hidden {
		fmt.Printf("Enter new contents for %s (input will be hidden): ", description)
		byteContent, err := term.ReadPassword(int(os.Stdin.Fd()))
		fmt.Println()
		if err != nil {
			log.Fatalf("Error reading hidden input: %v", err)
		}
		newContent = strings.TrimSpace(string(byteContent))
	} else {
		fmt.Printf("Enter new contents for %s: ", description)
		reader := bufio.NewReader(os.Stdin)
		text, err := reader.ReadString('\n')
		if err != nil {
			log.Fatalf("Error reading input: %v", err)
		}
		newContent = strings.TrimSpace(text)
	}

	// Write the new content to the file.
	err = ioutil.WriteFile(path, []byte(newContent+"\n"), 0644)
	if err != nil {
		fmt.Printf("Error writing to %s file at %s: %v\n", description, path, err)
	} else {
		fmt.Printf("%s file at %s has been updated.\n", description, path)
	}
	return newContent
}

// getDir extracts the directory from a full file path.
func getDir(filePath string) string {
	if idx := strings.LastIndex(filePath, `\`); idx != -1 {
		return filePath[:idx]
	}
	return "."
}

func main() {
	fmt.Println("Checking Restic repository and password files...\n")

	// Print current time for context.
	fmt.Printf("Current time: %s\n\n", time.Now().Format(time.RFC1123))

	repoContent := checkAndUpdateFile(REPO_PATH, "Restic repository", false)
	passwdContent := checkAndUpdateFile(PASSWD_PATH, "Restic password", true)

	// Summary of actions.
	fmt.Println("\nSummary of actions:")
	if repoContent != "" {
		fmt.Printf("- %s is set with: %s\n", REPO_PATH, repoContent)
	} else {
		fmt.Printf("- %s is empty or not set correctly.\n", REPO_PATH)
	}
	if passwdContent != "" {
		fmt.Printf("- %s is set (contents hidden).\n", PASSWD_PATH)
	} else {
		fmt.Printf("- %s is empty or not set correctly.\n", PASSWD_PATH)
	}

	fmt.Print("\nPlease run createPersephoneConfig.bat to continue. Press Enter to exit.")
	bufio.NewReader(os.Stdin).ReadBytes('\n')
}
