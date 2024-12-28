package infrastructure

import (
	"fmt"
	"os"
)

const promptFilename = "data/prompt.txt"

// GetPrompt reads the LLM prompt from the file and caches it.
func GetPrompt() (string, error) {
	data, err := os.ReadFile(promptFilename)
	if err != nil {
		return "", fmt.Errorf("error reading prompt file: %w", err)
	}

	return string(data), nil
}
