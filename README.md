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
    temperature=0.1,            # Lower temperature for more deterministic results
)

guard = ig.IntentGuard(options)
```

## Model

IntentGuard uses a custom 1B model fine-tuned from Llama-3.2-1B-Instruct, optimized specifically for code analysis and verification tasks. The model runs locally using [llamafile](https://github.com/Mozilla-Ocho/llamafile), ensuring privacy and fast inference.

## Contributing

## Local Development Environment Setup

To set up a local development environment for IntentGuard, follow these steps:

1. **Prerequisites:**
    - Ensure you have Python (version specified in Makefile, currently 3.10) installed on your system.
    - Install [Poetry](https://python-poetry.org/docs/#installation), a tool for dependency management and packaging in Python.

2. **Clone the repository:**
   ```bash
   git clone <repository_url>
   cd intentguard
   ```

3. **Install development dependencies:**
   ```bash
   make install
   ```
   This command uses Poetry to install all necessary development dependencies specified in `pyproject.toml`.

4. **Run tests and checks:**
   ```bash
   make test
   ```
   This command executes a comprehensive suite of checks including linting, formatting, type checking, and unit tests to ensure code quality.

### Useful development commands:

* `make install`: Installs development dependencies using Poetry.
* `make install-prod`: Installs only production dependencies.
* `make check`: Runs `ruff check` for linting.
* `make format-check`: Runs `ruff format --check` to check code formatting.
* `make mypy`: Runs `mypy` for static type checking.
* `make unittest`: Runs Python's built-in unittest framework.
* `make test`: Runs all checks and tests (linting, formatting, type checking, unit tests).
* `make clean`: Removes the virtual environment to start fresh.
* `make help`: Shows a list of available `make` commands and their descriptions.

Contributions are welcome! Check out our [roadmap](ROADMAP.md) for planned features.

## License

[MIT License](LICENSE)

---

IntentGuard is designed to complement, not replace, traditional testing approaches. It's most effective when used for complex code properties that are difficult to verify through conventional means.
