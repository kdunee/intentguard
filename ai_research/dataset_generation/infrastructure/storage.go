package infrastructure

import (
	"encoding/json"
	"github.com/kdunee/intentguard/dataset-generation/domain"
	"log"
	"os"
)

type OutputLine struct {
	Category string           `json:"category"`
	Examples []domain.Example `json:"examples"`
}

func WriteExamplesToOutput(category string, examples []domain.Example) {
	jsonBytes, err := json.Marshal(OutputLine{
		Category: category,
		Examples: examples,
	})
	if err != nil {
		log.Fatalf("Failed to marshal examples: %v", err)
	}

	f, err := os.OpenFile("output.jsonl", os.O_APPEND|os.O_CREATE|os.O_WRONLY, 0644)
	if err != nil {
		log.Fatalf("Failed to open output file: %v", err)
	}
	defer f.Close()

	_, err = f.WriteString(string(jsonBytes) + "\n")
	if err != nil {
		log.Fatalf("Failed to write to output file: %v", err)
	}
}
