# AILintTest

AILintTest is a Python testing library that uses Large Language Models to verify code properties through natural language assertions. It seamlessly integrates with popular testing frameworks like pytest and unittest, allowing developers to express complex code expectations in plain English while maintaining the structure of traditional test suites.

## Why AILintTest?

Traditional testing approaches often require extensive boilerplate code to verify complex properties. AILintTest bridges this gap by allowing developers to express sophisticated test cases in natural language, particularly useful for scenarios where writing conventional test code would be impractical or time-consuming.

### Key Features

1. **Natural Language Test Cases**: Write test assertions in plain English
2. **Framework Integration**: Works with pytest, unittest, and other testing frameworks
3. **Deterministic Results**: Uses voting mechanism and controlled sampling for consistent results
4. **Flexible Verification**: Test complex code properties that would be difficult to verify traditionally

## When to Use AILintTest

AILintTest is designed for scenarios where traditional test implementation would be impractical or require excessive code. For example:

```python
# Traditional approach would require:
# 1. Iterating through all methods
# 2. Parsing AST for each method
# 3. Checking exception handling patterns
# 4. Verifying logging calls
# 5. Maintaining complex test code

# With AILintTest:
def test_error_handling():
    ailint.assert_code(
        "All methods in {module} should use the custom ErrorHandler class for exception management, and log errors before re-raising them",
        {"module": my_critical_module}
    )

# Another example - checking documentation consistency
def test_docstring_completeness():
    ailint.assert_code(
        "All public methods in {module} should have docstrings that include Parameters, Returns, and Examples sections",
        {"module": my_api_module}
    )
```

## How It Works

### Deterministic Testing

AILintTest employs several mechanisms to ensure consistent and reliable results:

1. **Voting Mechanism**: Each assertion is evaluated multiple times (configurable through `quorum_size`), and the majority result is used
2. **Temperature Control**: Uses low temperature for LLM sampling to reduce randomness
3. **Structured Prompts**: Converts natural language assertions into structured prompts for consistent LLM interpretation

```python
# Configure determinism settings
options = AILintTestOptions(
    quorum_size=5,          # Number of evaluations per assertion
)
```

## Installation

```bash
pip install ailinttest
```

## Basic Usage

### With pytest

```python
from ailinttest import AILintTest

def test_code_properties():
    ailint = AILintTest()
    
    # Test code organization
    ailint.assert_code(
        "Classes in {module} should follow the Single Responsibility Principle",
        {"module": my_module}
    )
    
    # Test security practices
    ailint.assert_code(
        "All database queries in {module} should be parameterized to prevent SQL injection",
        {"module": db_module}
    )
```

### With unittest

```python
import unittest
from ailinttest import AILintTest

class TestCodeQuality(unittest.TestCase):
    def setUp(self):
        self.ailint = AILintTest()
    
    def test_error_handling(self):
        self.ailint.assert_code(
            "All API endpoints in {module} should have proper input validation",
            {"module": api_module}
        )
```

## Advanced Usage

### Custom Evaluation Options

```python
from ailinttest import AILintTest, AILintTestOptions

options = AILintTestOptions(
    quorum_size=7,              # Increase voting sample size
    model="gpt-4o-2024-08-06",  # Use a more capable model
)

ailint = AILintTest(options)
```

## Contributing

Contributions are welcome!

## License

[MIT License](LICENSE)

## Acknowledgements

This project uses [LiteLLM](https://github.com/BerriAI/litellm) for LLM integration.

---

AILintTest is designed to complement, not replace, traditional testing approaches. It's most effective when used for complex code properties that are difficult to verify through conventional means.
