import random

_ITEMS = [
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
]


def get_random_category() -> str:
    return random.choice(_ITEMS)
