package main

import (
	"bufio"
	"fmt"
	"os"
	"strings"
)

// Config file path
const configFilePath = ".persephone.conf"

// Read configuration file into a map
func readConfig() (map[string]string, error) {
	config := make(map[string]string)

	file, err := os.Open(configFilePath)
	if err != nil {
		return config, err
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
		value := strings.Trim(strings.TrimSpace(parts[1]), "\"") // Remove quotes
		config[key] = value
	}

	return config, scanner.Err()
}

// Write updated config back to the file
func writeConfig(config map[string]string) error {
	file, err := os.Create(configFilePath)
	if err != nil {
		return err
	}
	defer file.Close()

	for key, value := range config {
		_, err := fmt.Fprintf(file, "%s=\"%s\"\n", key, value)
		if err != nil {
			return err
		}
	}
	return nil
}

// Display all key-value pairs
func showConfig(config map[string]string) {
	fmt.Println("Current Persephone Configuration:")
	for key, value := range config {
		fmt.Printf("%s=\"%s\"\n", key, value)
	}
}

// Get user input
func getUserInput(prompt string) string {
	fmt.Print(prompt)
	scanner := bufio.NewScanner(os.Stdin)
	scanner.Scan()
	return strings.TrimSpace(scanner.Text())
}

func main() {
	config, err := readConfig()
	if err != nil {
		fmt.Println("Error reading config:", err)
		return
	}

	for {
		fmt.Println("\nChoose an option:")
		fmt.Println("1. Read configuration")
		fmt.Println("2. Create or update a key")
		fmt.Println("3. Delete a key")
		fmt.Println("4. Exit")
		choice := getUserInput("Enter choice: ")

		switch choice {
		case "1":
			showConfig(config)

		case "2":
			key := getUserInput("Enter key to create/update: ")
			value := getUserInput("Enter value: ")
			config[key] = value
			err := writeConfig(config)
			if err != nil {
				fmt.Println("Error updating config:", err)
			} else {
				fmt.Println("Config updated successfully.")
			}

		case "3":
			key := getUserInput("Enter key to delete: ")
			if _, exists := config[key]; exists {
				delete(config, key)
				err := writeConfig(config)
				if err != nil {
					fmt.Println("Error deleting key:", err)
				} else {
					fmt.Println("Key deleted successfully.")
				}
			} else {
				fmt.Println("Key not found.")
			}

		case "4":
			fmt.Println("Exiting.")
			return

		default:
			fmt.Println("Invalid choice. Try again.")
		}
	}
}
