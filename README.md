# LLM Static Assert

LLM Static Assert is a powerful Python library that leverages Language Models (LLMs) to perform static assertions on code. This innovative approach combines the flexibility of natural language with the rigor of static analysis, offering a unique solution for code quality and correctness verification.

## Why LLM Static Assert?

Traditional static analysis tools often struggle with complex, context-dependent code properties. LLM Static Assert bridges this gap by utilizing the advanced reasoning capabilities of large language models to evaluate code against natural language expectations.

### Benefits

1. **Natural Language Assertions**: Express complex code properties and expectations using plain English, making it easier to write and understand assertions.
2. **Flexibility**: Evaluate a wide range of code properties that might be challenging for traditional static analysis tools.
3. **Context-Aware**: LLMs can consider broader context and nuanced relationships within the code.
4. **Customizable**: Adjust the assertion process with options like quorum size and model selection.

### Drawbacks

1. **Computational Overhead**: LLM inference can be more resource-intensive than traditional static analysis.
2. **Potential for Ambiguity**: Natural language assertions may sometimes lead to ambiguous interpretations.
3. **Dependence on LLM Quality**: The effectiveness of assertions relies on the capabilities of the underlying language model.

## When to Use LLM Static Assert

- When you need to verify complex, context-dependent code properties.
- For catching subtle logical errors that might escape traditional static analysis.
- In projects where code correctness is critical, and you want an additional layer of verification.
- When you want to express code expectations in a more natural, readable format.

## When Not to Use LLM Static Assert

- For simple, straightforward assertions that can be easily handled by traditional unit tests or type checkers.
- In environments where computational resources are severely constrained.
- When you need deterministic, 100% reproducible results (due to the potential variability in LLM outputs).

## Installation

You can install LLM Static Assert using pip:

```bash
pip install llm-static-assert
```

Or if you're using Poetry:

```bash
poetry add llm-static-assert
```

## Usage

Here's a basic example of how to use LLM Static Assert:

```python
from llm_static_assert import LLMStaticAssert, LLMStaticAssertOptions

# Create an instance of LLMStaticAssert with custom options
options = LLMStaticAssertOptions(quorum_size=3, model="gpt-4o-mini")
lsa = LLMStaticAssert(options)

# Define a class or function you want to assert about
class MyClass:
    def some_method(self):
        pass

# Perform a static assertion
lsa.static_assert(
    "{class} should have a method named 'some_method'",
    {"class": MyClass}
)
```

In this example, we're asserting that `MyClass` has a method named `some_method`. The LLM will analyze the provided class and evaluate whether it meets this expectation.

### Advanced Usage

You can customize the assertion process by adjusting the `LLMStaticAssertOptions`:

```python
options = LLMStaticAssertOptions(
    quorum_size=5,  # Perform 5 inferences and use majority voting
    model="gpt-4"   # Use a more advanced model for complex assertions
)
lsa = LLMStaticAssert(options)

# You can also provide custom options for a specific assertion
lsa.static_assert(
    "{class} should implement proper error handling in all methods",
    {"class": MyComplexClass},
    options=LLMStaticAssertOptions(quorum_size=7, model="gpt-4")
)
```

## Contributing

Contributions to LLM Static Assert are welcome! Please refer to the project's issues page on GitHub for areas where help is needed or to suggest improvements.

## License

[MIT License](LICENSE)

## Acknowledgements

This project uses [LiteLLM](https://github.com/BerriAI/litellm) for LLM integration.

---

LLM Static Assert is an experimental tool and should be used in conjunction with, not as a replacement for, traditional testing and static analysis methods. Always validate its results and use it responsibly.
