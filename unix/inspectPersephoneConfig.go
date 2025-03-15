package main

import (
	"fmt"
	"os"
	"path/filepath"
	"strings"
	"time"
)

// inspectDirectory walks through the given root directory and outputs matching files/directories.
func inspectDirectory(root string) {
	err := filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			fmt.Printf("Error accessing %q: %v\n", path, err)
			return nil // continue walking even if there's an error
		}
		name := info.Name()
		if name == ".persephone.conf" ||
			strings.Contains(name, "persephone") ||
			
			itemType := "File"
			if info.IsDir() {
				itemType = "Directory"
			}
			
			modTime := info.ModTime().Format("2006-01-02 15:04:05")
			
			fmt.Printf("%s: %s\n  Size: %d bytes\n  Last Modified: %s\n\n",
				itemType, path, info.Size(), modTime)
		}
		return nil
	})
	if err != nil {
		fmt.Printf("Error walking the path %q: %v\n", root, err)
	}
}

func main() {
	// List of directories to search.
	roots := []string{"/home", "/opt", "/root", "/srv", "/usr", "/etc", "/var", "/tmp"}
	
	for _, root := range roots {
		// Check if the directory exists before attempting to walk it.
		if stat, err := os.Stat(root); err != nil || !stat.IsDir() {
			fmt.Printf("Directory %s does not exist or is not accessible, skipping.\n", root)
			continue
		}
		fmt.Printf("Searching in %s...\n", root)
		startTime := time.Now()
		inspectDirectory(root)
		fmt.Printf("Finished searching %s (took %s)\n\n", root, time.Since(startTime))
	}
}
