package main

import (
	"fmt"
	"io"
	"os"
	"os/exec"
	"path/filepath"
	"strings"
)

const (
	outputFile = "excluded_dirs.txt"
	maxDepth   = 5 // adjust as needed; this mimics -maxdepth 5 in your find command
)

func main() {
	// Open the output file for writing (truncate if exists)
	f, err := os.Create(outputFile)
	if err != nil {
		fmt.Fprintf(os.Stderr, "Error creating output file: %v\n", err)
		os.Exit(1)
	}
	defer f.Close()

	// Walk through directories starting from "/" with a limit on depth.
	root := "/"
	err = filepath.Walk(root, func(path string, info os.FileInfo, err error) error {
		if err != nil {
			// Skip directories/files that can't be accessed.
			return nil
		}

		// Only process directories.
		if !info.IsDir() {
			return nil
		}

		// Calculate current depth.
		depth := strings.Count(path, string(os.PathSeparator))
		if depth > maxDepth {
			// If the depth is greater than maxDepth, skip walking into this directory.
			return filepath.SkipDir
		}

		// Run the tmutil command.
		cmd := exec.Command("tmutil", "isexcluded", path)
		output, err := cmd.CombinedOutput()
		// Ignore errors from tmutil to mimic 2>/dev/null in bash.
		if err != nil && len(output) == 0 {
			return nil
		}

		// Check if the output contains "Excluded"
		if strings.Contains(string(output), "Excluded") {
			// Write the directory path to the file.
			_, err := io.WriteString(f, path+"\n")
			if err != nil {
				fmt.Fprintf(os.Stderr, "Error writing to file: %v\n", err)
			}
		}

		return nil
	})

	if err != nil {
		fmt.Fprintf(os.Stderr, "Error walking the path: %v\n", err)
		os.Exit(1)
	}

	fmt.Printf("Excluded directories have been stored in %s\n", outputFile)
}
