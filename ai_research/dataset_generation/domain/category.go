package domain

import "math/rand"

var items = []string{
	"Code Expressiveness",
	"Design Patterns",
	"Maintainability",
	"Security",
	"Testability",
	"Architecture",
	"Standards Conformance",
	"Error Handling",
	"Documentation",
	"API Design",
	"Code Style",
	"Business Logic",
	"Miscellaneous",
	"Function/Method Calls and Arguments",
	"Variable Scope and Lifetime",
	"Control Flow Understanding",
}

func GetRandomCategory() string {
	return items[rand.Intn(len(items))]
}
