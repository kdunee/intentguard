package domain

import (
	"fmt"
	"testing"
)

const assertionTextExample = `"{user_service} should use dependency injection for {logger} and {database} to improve modularity and testability"`

func Example_parseAssertionExtractsAssertionText() {
	assertion := parseAssertion(assertionTextExample)
	fmt.Println(assertion.AssertionText)

	// Output:
	// {user_service} should use dependency injection for {logger} and {database} to improve modularity and testability
}

func Test_parseAssertion_ExtractsCodeObjectNames(t *testing.T) {
	assertion := parseAssertion(assertionTextExample)
	if len(assertion.CodeObjectNames) != 3 {
		t.Errorf("Expected 2 code object names, got %d", len(assertion.CodeObjectNames))
	}
	expectedNames := []string{"user_service", "logger", "database"}
	for i, expectedName := range expectedNames {
		if assertion.CodeObjectNames[i] != expectedName {
			t.Errorf("Expected code object name to be %s, got %s", expectedName, assertion.CodeObjectNames[i])
		}
	}
}

func Test_parseAssertion_ExtractsEmptyCodeObjectNames(t *testing.T) {
	assertion := parseAssertion("")
	if len(assertion.CodeObjectNames) != 0 {
		t.Errorf("Expected 0 code object names, got %d", len(assertion.CodeObjectNames))
	}
}
