package domain

import (
	"encoding/json"
	"regexp"
	"strings"
)

type Assertion struct {
	AssertionText   string
	CodeObjectNames []string
}

func parseAssertion(assertionText string) Assertion {
	re := regexp.MustCompile(`\{(?P<object>[^}]*)}`)

	trimmedAssertionText := strings.Trim(assertionText, `"`)

	matches := re.FindAllStringSubmatch(assertionText, -1)
	if matches != nil {
		codeObjectNames := make([]string, len(matches))
		for i, match := range matches {
			codeObjectNames[i] = match[re.SubexpIndex("object")]
		}
		return Assertion{
			AssertionText:   trimmedAssertionText,
			CodeObjectNames: codeObjectNames,
		}
	}

	return Assertion{
		AssertionText:   trimmedAssertionText,
		CodeObjectNames: []string{},
	}
}

func (p Assertion) MarshalJSON() ([]byte, error) {
	return json.Marshal(map[string]interface{}{
		"assertionText":   p.AssertionText,
		"codeObjectNames": p.CodeObjectNames,
	})
}
