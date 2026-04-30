<div align="center">
    <img alt="intentguard" height="200px" src="https://raw.githubusercontent.com/kdunee/intentguard/refs/heads/main/design/logomark-256.png">
</div>

# IntentGuard

![GitHub Sponsors](https://img.shields.io/github/sponsors/kdunee)
![PyPI - Downloads](https://static.pepy.tech/badge/intentguard)
![GitHub License](https://img.shields.io/github/license/kdunee/intentguard)
![PyPI - Version](https://img.shields.io/pypi/v/intentguard)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/intentguard)

IntentGuard lets you test code intent with natural language assertions.

Use it when a property is real and test-worthy, but awkward to encode with ordinary assertions: architecture rules, security practices, documentation contracts, error-handling conventions, or other cross-cutting code qualities. IntentGuard checks referenced code with a local model and raises `AssertionError` when the judgement fails.

IntentGuard complements traditional tests. Keep unit tests for exact outputs, edge cases, state changes, and safety-critical behavior. Use IntentGuard where a custom AST walk, linter rule, or review checklist would be noisy or expensive.

> [!IMPORTANT]
> The current default model is `IntentGuard-1-qwen2.5-coder-1.5b`, with 92.5% accuracy and 92.3% precision in the validation suite.

## Installation

```bash
pip install intentguard
```

## Quick Start

### With pytest

```python
import intentguard as ig

def test_code_properties():
    guard = ig.IntentGuard()

    guard.assert_code(
        "Classes in {module} should follow the Single Responsibility Principle",
        {"module": my_module}
    )

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

## Good Fits

IntentGuard works best for high-level properties that are easy to describe and hard to check directly:

* "All public methods in {module} should have docstrings with Parameters and Returns sections."
* "All API endpoints in {module} should validate input before using it."
* "All methods in {module} should log errors before re-raising them."

Avoid using it for exact numeric results, runtime behavior that must be executed, or anything that needs perfect determinism. Model judgement is useful signal, not proof.

## How It Works

1. `assert_code()` receives a natural language assertion and code references.
2. Code references are converted into source snippets.
3. IntentGuard builds a structured prompt and checks the cache.
4. On cache miss, the local model evaluates the assertion `num_evaluations` times.
5. A strict majority decides the result. Ties fail.
6. The result is cached for repeat runs.

## Near-Deterministic Results

IntentGuard is designed for repeatable judgements, not guaranteed determinism. It uses low-temperature sampling, repeated evaluation, strict majority voting, and caching to make results stable in normal test runs. Fresh model evaluations can still vary, especially after changing the assertion, code, model, temperature, or evaluation count.

Configure repeatability:

```python
import intentguard as ig

options = ig.IntentGuardOptions(
    num_evaluations=7,  # More evaluations make majority vote more stable
    temperature=0.1,    # Lower temperature reduces sampling variance
)

guard = ig.IntentGuard(options)
```

## Model

IntentGuard uses [a custom 1.5B parameter model](https://huggingface.co/kdunee/IntentGuard-1-qwen2.5-coder-1.5b-gguf), fine-tuned from Qwen2.5-Coder-1.5B for code property verification. It runs locally through [llamafile](https://github.com/mozilla-ai/llamafile), so code is not sent to a hosted API by default.

## Performance

| Model                                                | Accuracy | Precision | Recall |
|------------------------------------------------------|----------|-----------|--------|
| **(current model)** IntentGuard-1-qwen2.5-coder-1.5b | 92.5%    | 92.3%     | 89.4%  |
| (previous model)    IntentGuard-1-llama3.2-1b        | 92.4%    | 91.0%     | 91.0%  |
| (reference model)   gpt-4o-mini                      | 89.3%    | 85.3%     | 90.2%  |

### Validation Methodology

The validation suite is intentionally strict:

* Each test example gets 15 total evaluations (5 trials x 3 evaluations per trial)
* A voting mechanism is applied within each group (jury size = 3)
* A test passes only if all 5 trials succeed with majority agreement (2 out of 3 or better)

For more details, see the [validation documentation](validation/README.md).

## Compatibility

IntentGuard requires Python 3.10+. OS and architecture support come from [llamafile](https://github.com/mozilla-ai/llamafile):

* Linux 2.6.18+
* macOS 23.1.0+ (GPU support on ARM64)
* Windows 10+ (AMD64)
* FreeBSD 13+
* NetBSD 9.2+ (AMD64)
* OpenBSD 7+ (AMD64)

## Local Development Environment Setup

1. **Prerequisites:** Python 3.10+, [uv](https://docs.astral.sh/uv/).
2. **Clone:** `git clone <repository_url> && cd intentguard`
3. **Install dev dependencies:** `make install` or `uv sync --dev --group validation --group dataset`
4. **Run tests & checks:** `make test`

Useful commands:

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
