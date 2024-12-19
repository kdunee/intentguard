package domain

import (
	"log"
	"regexp"
	"strings"
)

func ParseExamples(response string) []Example {
	exampleSections := parseExampleSections(response)
	examples := make([]Example, 0, len(exampleSections))
	for _, section := range exampleSections {
		example, err := parseExample(section)
		if err != nil {
			log.Printf("Failed to parse example, skipping: %v", err)
			continue
		}
		examples = append(examples, example)
	}
	return examples
}

func parseExampleSections(response string) []string {
	re := regexp.MustCompile(`### .*Example.*\n\s*`)

	// Find all headers
	matches := re.FindAllStringSubmatchIndex(response, -1)

	sections := make([]string, len(matches))

	// Extract content between headers
	for i := 0; i < len(matches)-1; i++ {
		start := matches[i][1] // End of the current header
		end := matches[i+1][0] // Start of the next header
		section := strings.TrimSpace(response[start:end])
		sections[i] = section
	}

	// Extract content after the last header
	if len(matches) > 0 {
		start := matches[len(matches)-1][1] // End of the last header
		section := strings.TrimSpace(response[start:])
		sections[len(matches)-1] = section
	}

	return sections
}
