package infrastructure

import (
	"fmt"
	"os"
)

const (
	generationPromptFile = "data/prompt.txt"
	filteringPromptFile = "data/filtering.txt"
)

// GetGenerationPrompt reads the generation LLM prompt from the file.
func GetGenerationPrompt() (string, error) {
	data, err := os.ReadFile(generationPromptFile)
	if err != nil {
		return "", fmt.Errorf("error reading generation prompt file: %w", err)
	}
	return string(data), nil
}

// GetFilteringPrompt reads the filtering LLM prompt from the file.
func GetFilteringPrompt() (string, error) {
	data, err := os.ReadFile(filteringPromptFile)
	if err != nil {
		return "", fmt.Errorf("error reading filtering prompt file: %w", err)
	}
	return string(data), nil
}
