<div align="center">
    <img alt="intentguard" height="200px" src="./design/logomark-256.png">
</div>

# IntentGuard

![GitHub Sponsors](https://img.shields.io/github/sponsors/kdunee)
![PyPI - Downloads](https://static.pepy.tech/badge/intentguard)
![GitHub License](https://img.shields.io/github/license/kdunee/intentguard)
![PyPI - Version](https://img.shields.io/pypi/v/intentguard)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/intentguard)


IntentGuard is a Python library for verifying code properties using natural language assertions. It integrates with testing frameworks like pytest and unittest, allowing you to express complex code expectations in plain English within your existing test suites.

## Why IntentGuard?

Traditional code testing often requires writing extensive code to verify intricate properties. IntentGuard simplifies this by enabling you to express sophisticated test cases in natural language. This is particularly useful when writing conventional test code becomes impractical or overly complex.

**Key Use Cases:**

* **Complex Property Verification:** Test intricate code behaviors that are hard to assert with standard methods.
* **Reduced Boilerplate:**  Avoid writing lengthy test code for advanced checks.
* **Improved Readability:** Natural language assertions make tests easier to understand, especially for complex logic.

### Key Features

1. **Natural Language Assertions:** Write test assertions in plain English.
2. **Testing Framework Integration:** Works seamlessly with pytest and unittest.
3. **Deterministic Results:** Employs a voting mechanism and controlled sampling for consistent test outcomes.
4. **Flexible Verification:** Test properties difficult to verify using traditional techniques.
5. **Detailed Failure Explanations:** Provides clear, natural language explanations when assertions fail.
6. **Efficient Result Caching:** Caches results to speed up test execution and avoid redundant evaluations.

## When to Use IntentGuard

IntentGuard is ideal when implementing traditional tests for certain code properties is challenging or requires excessive code. Consider these scenarios:

```python
# Example 1: Error Handling Verification

def test_error_handling():
    ig.assert_code(
        "All methods in {module} should use the custom ErrorHandler class for exception management, and log errors before re-raising them",
        {"module": my_critical_module}
    )


# Example 2: Documentation Consistency Check

def test_docstring_completeness():
    ig.assert_code(
        "All public methods in {module} should have docstrings that include Parameters, Returns, and Examples sections",
        {"module": my_api_module}
    )
````

In these examples, manually writing tests to iterate through methods, parse AST, and check for specific patterns would be significantly more complex than using IntentGuard's natural language assertions.

## How It Works: Deterministic Testing

IntentGuard ensures reliable results through these mechanisms:

1.  **Voting Mechanism:** Each assertion is evaluated multiple times (configurable via `num_evaluations`), and the majority result determines the outcome.
2.  **Temperature Control:** Low temperature sampling in the LLM minimizes randomness.
3.  **Structured Prompts:** Natural language assertions are converted into structured prompts for consistent LLM interpretation.

You can configure determinism settings:

```python
options = IntentGuardOptions(
    num_evaluations=5,      # Number of evaluations per assertion
)
```

## Compatibility

IntentGuard is compatible with:

  * **Python:** 3.10+
  * **Operating Systems:**
      * Linux 2.6.18+ (most distributions since \~2007)
      * Darwin (macOS) 23.1.0+ (GPU support only on ARM64)
      * Windows 10+ (AMD64 only)
      * FreeBSD 13+
      * NetBSD 9.2+ (AMD64 only)
      * OpenBSD 7+ (AMD64 only)

These OS and architecture compatibilities are inherited from [llamafile](https://github.com/Mozilla-Ocho/llamafile), which IntentGuard uses to run the model locally.

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

## Advanced Usage: Custom Evaluation Options

```python
import intentguard as ig

options = ig.IntentGuardOptions(
    num_evaluations=7,          # Increase number of evaluations
    temperature=0.1,            # Lower temperature for more deterministic results
)

guard = ig.IntentGuard(options)
```

## Model

IntentGuard utilizes [a custom 1B parameter model](https://huggingface.co/kdunee/IntentGuard-1), fine-tuned from Llama-3.2-1B-Instruct. This model is optimized for code analysis and verification and runs locally using [llamafile](https://github.com/Mozilla-Ocho/llamafile) for privacy and efficient inference.

## Local Development Environment Setup

To contribute to IntentGuard, set up your local environment:

1.  **Prerequisites:** Python 3.10+, [Poetry](https://python-poetry.org/docs/#installation).
2.  **Clone:** `git clone <repository_url> && cd intentguard`
3.  **Install dev dependencies:** `make install`
4.  **Run tests & checks:** `make test`

Refer to the `Makefile` for more development commands.

### Useful development commands:

  * `make install`: Installs development dependencies.
  * `make install-prod`: Installs production dependencies only.
  * `make check`: Runs linting checks (`ruff check`).
  * `make format-check`: Checks code formatting (`ruff format --check`).
  * `make mypy`: Runs static type checking (`mypy`).
  * `make unittest`: Runs unit tests.
  * `make test`: Runs all checks and tests.
  * `make clean`: Removes the virtual environment.
  * `make help`: Lists available `make` commands.

## License

[MIT License](LICENSE)

-----

IntentGuard is a complementary tool for specific testing needs, not a replacement for traditional testing. It is most effective for verifying complex code properties that are difficult to test conventionally.
