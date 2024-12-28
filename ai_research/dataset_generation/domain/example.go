package domain

import (
	"encoding/json"
	"fmt"
	"regexp"
	"strings"
)

type Example struct {
	Assertion   Assertion
	CodeObjects []CodeObject
	Thoughts    string
	Explanation *string
}

func parseExample(exampleSection string) (Example, error) {
	assertionText, err := parseAssertionText(exampleSection)
	if err != nil {
		return Example{}, err
	}

	assertion := parseAssertion(assertionText)

	codeSection, err := parseCodeSection(exampleSection)
	if err != nil {
		return Example{}, err
	}

	thoughts, err := parseThoughts(exampleSection)
	if err != nil {
		return Example{}, err
	}

	explanation := parseExplanation(exampleSection)

	codeObjects := parseCodeObjects(codeSection)

	validationErr := validateExample(assertion, codeObjects, explanation)
	if validationErr != nil {
		return Example{}, validationErr
	}

	return Example{
		Assertion:   assertion,
		CodeObjects: codeObjects,
		Thoughts:    thoughts,
		Explanation: explanation,
	}, nil
}

func validateExample(assertion Assertion, codeObjects []CodeObject, explanation *string) error {
	if len(assertion.CodeObjectNames) != len(codeObjects) {
		return fmt.Errorf("number of code objects does not match number of code object names in assertion")
	}

	codeObjectNames := make(map[string]bool)
	for _, codeObject := range codeObjects {
		codeObjectNames[codeObject.Name] = true
	}
	for _, name := range assertion.CodeObjectNames {
		if !codeObjectNames[name] {
			return fmt.Errorf("code object %s is referenced in assertion but not in code section", name)
		}
	}

	if explanation != nil {
		lowerExplanation := strings.ToLower(*explanation)
		if strings.Contains(lowerExplanation, "example") || strings.Contains(lowerExplanation, "positive") {
			return fmt.Errorf("explanation contains forbidden words 'example' or 'positive'")
		}
	}

	return nil
}

func parseExplanation(exampleSection string) *string {
	re := regexp.MustCompile(`\[Explanation]\s*(?P<explanation>[\w\W]*?)((### Example)|(\n\n)|\z)`)

	match := re.FindStringSubmatch(exampleSection)
	if match == nil {
		return nil
	}

	result := strings.TrimRight(match[re.SubexpIndex("explanation")], " \t\n\r")
	return &result
}

func parseCodeObjects(codeSection string) []CodeObject {
	re := regexp.MustCompile(`\{(?P<name>[^}]*)}:\s*` + "```" + `python\s*(?P<code>[\W\w]*?)` + "```")

	matches := re.FindAllStringSubmatch(codeSection, -1)
	if matches != nil {
		codeObjects := make([]CodeObject, len(matches))
		for i, match := range matches {
			codeObjects[i] = CodeObject{
				Name: match[re.SubexpIndex("name")],
				Code: match[re.SubexpIndex("code")],
			}
		}
		return codeObjects
	}

	return []CodeObject{}
}

func parseThoughts(exampleSection string) (string, error) {
	re := regexp.MustCompile(`\[Thinking]\s*(?P<thoughts>[\w\W]*?)((\[Explanation])|\z)`)

	match := re.FindStringSubmatch(exampleSection)
	if match == nil {
		return "", fmt.Errorf("failed to find thoughts in example: %s", exampleSection)
	}
	return strings.TrimRight(match[re.SubexpIndex("thoughts")], " \t\n\r"), nil
}

func parseCodeSection(exampleSection string) (string, error) {
	re := regexp.MustCompile(`\[Code]\s*(?P<code>[\w\W]*?)\[Thinking]`)

	match := re.FindStringSubmatch(exampleSection)
	if match == nil {
		return "", fmt.Errorf("failed to find code section in example: %s", exampleSection)
	}
	return strings.TrimRight(match[re.SubexpIndex("code")], " \t\n\r"), nil
}

func parseAssertionText(exampleSection string) (string, error) {
	re := regexp.MustCompile(`\[Assertion]\s*(?P<assertion>[\w\W]*?)\[Code]`)

	match := re.FindStringSubmatch(exampleSection)
	if match == nil {
		return "", fmt.Errorf("failed to find assertion in example: %s", exampleSection)
	}
	return strings.TrimRight(match[re.SubexpIndex("assertion")], " \t\n\r"), nil
}

func (p Example) MarshalJSON() ([]byte, error) {
	return json.Marshal(map[string]interface{}{
		"assertion":   p.Assertion,
		"codeObjects": p.CodeObjects,
		"thoughts":    p.Thoughts,
		"explanation": p.Explanation,
	})
}
