package main

import (
	"fmt"
	"log"
	"os"
	"os/exec"
	"os/user"
)

const (
	SRV_DIR = "/srv/codeMonkeyCyber" // Directory where Restic repos will live
	// LOG_DIR is defined in the Python script but not used further.
	LOG_DIR = "/var/log/codeMonkeyCyber"
)

// runCommand executes the command specified by args and propagates any errors.
func runCommand(args []string) error {
	cmd := exec.Command(args[0], args[1:]...)
	cmd.Stdout = os.Stdout
	cmd.Stderr = os.Stderr
	return cmd.Run()
}

func main() {
	fmt.Println("Setting up backup repository on server...\n")

	// 1. Create server directory for backups.
	if err := runCommand([]string{"sudo", "mkdir", "-p", SRV_DIR}); err != nil {
		log.Fatalf("Error creating directory: %v", err)
	}

	// 2. Secure ownership & permissions.
	if err := runCommand([]string{"sudo", "chown", "-R", "root:root", SRV_DIR}); err != nil {
		log.Fatalf("Error setting ownership: %v", err)
	}

	// 700 ensures only root can access the directory; note that chmod 600 sets read-write for owner.
	if err := runCommand([]string{"sudo", "chmod", "600", SRV_DIR}); err != nil {
		log.Fatalf("Error setting permissions: %v", err)
	}

	fmt.Printf("Server repository directory set up at %s with restricted permissions.\n\n", SRV_DIR)

	// Get server user and hostname.
	currentUser, err := user.Current()
	if err != nil {
		log.Fatalf("Error getting current user: %v", err)
	}
	persSrvUser := currentUser.Username

	persSrvHostname, err := os.Hostname()
	if err != nil {
		log.Fatalf("Error getting hostname: %v", err)
	}

	fmt.Printf("This server is located at %s@%s:%s\n", persSrvUser, persSrvHostname, SRV_DIR)
	fmt.Println("It is important you note this down somewhere.")
	fmt.Println("You will use it when running `./createPersephoneClient.sh`")
	fmt.Println("It's also generally a good idea to know where your backups are stored.")
}
