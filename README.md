# IntentGuard

![GitHub Sponsors](https://img.shields.io/github/sponsors/kdunee)
![PyPI - Downloads](https://static.pepy.tech/badge/intentguard)
![GitHub License](https://img.shields.io/github/license/kdunee/intentguard)
![PyPI - Version](https://img.shields.io/pypi/v/intentguard)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/intentguard)


IntentGuard is a Python library for verifying code properties using natural language assertions. It seamlessly integrates with popular testing frameworks like pytest and unittest, allowing developers to express complex code expectations in plain English while maintaining the structure of traditional test suites.

## Why IntentGuard?

Traditional testing approaches often require extensive boilerplate code to verify complex properties. IntentGuard bridges this gap by allowing developers to express sophisticated test cases in natural language, particularly useful for scenarios where writing conventional test code would be impractical or time-consuming.

### Key Features

1. **Natural Language Test Cases:** Write test assertions in plain English.
2. **Framework Integration:** Works with pytest, unittest, and other testing frameworks.
3. **Deterministic Results:** Uses a voting mechanism and controlled sampling for consistent results.
4. **Flexible Verification:** Test complex code properties that would be difficult to verify traditionally.
5. **Detailed Failure Explanations:** Provides clear explanations when assertions fail, helping you understand the root cause and fix issues faster.
6. **Efficient Result Caching:** Caches assertion results to avoid redundant processing and speed up test execution.

## When to Use IntentGuard

IntentGuard is designed for scenarios where traditional test implementation would be impractical or require excessive code. For example:

```python
# Traditional approach would require:
# 1. Iterating through all methods
# 2. Parsing AST for each method
# 3. Checking exception handling patterns
# 4. Verifying logging calls
# 5. Maintaining complex test code

# With IntentGuard:
def test_error_handling():
    ig.assert_code(
        "All methods in {module} should use the custom ErrorHandler class for exception management, and log errors before re-raising them",
        {"module": my_critical_module}
    )

# Another example - checking documentation consistency
def test_docstring_completeness():
    ig.assert_code(
        "All public methods in {module} should have docstrings that include Parameters, Returns, and Examples sections",
        {"module": my_api_module}
    )
```

## How It Works

### Deterministic Testing

IntentGuard employs several mechanisms to ensure consistent and reliable results:

1. **Voting Mechanism**: Each assertion is evaluated multiple times (configurable through `num_evaluations`), and the majority result is used
2. **Temperature Control**: Uses low temperature for LLM sampling to reduce randomness
3. **Structured Prompts**: Converts natural language assertions into structured prompts for consistent LLM interpretation

```python
# Configure determinism settings
options = IntentGuardOptions(
    num_evaluations=5,      # Number of evaluations per assertion
)
```

## Installation

```bash
pip install intentguard
```

## Basic Usage

### With pytest

```python
import intentguard as ig

def test_code_properties():
    guard = ig.IntentGuard()
    
    # Test code organization
    guard.assert_code(
        "Classes in {module} should follow the Single Responsibility Principle",
        {"module": my_module}
    )
    
    # Test security practices
    guard.assert_code(
        "All database queries in {module} should be parameterized to prevent SQL injection",
        {"module": db_module}
    )
```

### With unittest

```python
import unittest
import intentguard as ig

class TestCodeQuality(unittest.TestCase):
    def setUp(self):
        self.guard = ig.IntentGuard()
    
    def test_error_handling(self):
        self.guard.assert_code(
            "All API endpoints in {module} should have proper input validation",
            {"module": api_module}
        )
```

## Advanced Usage

### Custom Evaluation Options

```python
import intentguard as ig

options = ig.IntentGuardOptions(
    num_evaluations=7,          # Increase number of evaluations
    model="gpt-4o-2024-08-06",  # Use a more capable model
)

guard = ig.IntentGuard(options)
```

## Contributing

Contributions are welcome! Check out our [roadmap](ROADMAP.md) for planned features.

## License

[MIT License](LICENSE)

## Acknowledgements

This project uses [LiteLLM](https://github.com/BerriAI/litellm) for LLM integration.

---

IntentGuard is designed to complement, not replace, traditional testing approaches. It's most effective when used for complex code properties that are difficult to verify through conventional means.
