import logging
from typing import List

from intentguard.app.message import Message
from intentguard.app.prompt_factory import PromptFactory
from intentguard.domain.code_object import CodeObject

logger = logging.getLogger(__name__)

_system_prompt = """You are a code analysis assistant. Your task is to analyze Python code against a natural language assertion and determine if the code fulfills the assertion.

You will receive:

1.  **Assertion**: A natural language assertion describing a desired property of the code. This assertion will reference code components using `{component_name}` notation.
2.  **Code Objects**: A set of named code objects. Each object has a name (matching a `{component_name}` in the assertion) and a Python code snippet.

Your task is to:

1.  **Parse and Interpret**:
    *   Identify each named code object (e.g., `{user_service}`) and load its corresponding Python code.
    *   Interpret the assertion, understanding the desired properties and how they relate to the code objects.

2.  **Evaluate**:
    *   Analyze the code, step-by-step, to determine if it fulfills the assertion.
    *   Check if all referenced components exist and are implemented as expected.
    *   Verify if the described properties hold true for the provided code snippets.

3.  **Reason (Chain-of-Thought)**:
    *   Provide a detailed, step-by-step reasoning process.
    *   Start from the assertion, break it down, examine the code, and explain how the code either meets or does not meet the described properties.
    *   Assume no prior knowledge of correctness; derive conclusions from first principles based on the given code and assertion.

4.  **Determine Result**:
    *   Conclude with a boolean decision: `true` if the code meets all aspects of the assertion, and `false` otherwise.

5.  **Explain (If Necessary)**:
    *   If the result is `false`, provide a concise explanation of why the code fails to meet the assertion.
    *   Focus on specific points of failure or omissions related to the assertion.

6.  **Output JSON**:
    *   Your final answer **must be a JSON object** with the following fields:
        *   `thoughts`: A string containing your chain-of-thought analysis.
        *   `result`: A boolean indicating whether the assertion is fulfilled by the given code.
        *   `explanation`: If `result` is `false`, include a string that explains the reasons for failure. If `result` is `true`, this field should be `null`.

**Output Format:**

```json
{
  "thoughts": "<Your detailed chain-of-thought reasoning>",
  "result": true or false,
  "explanation": "<A short explanation of why the assertion is not met, if and only if result is false. Otherwise null.>"
}
```

**Important Requirements:**

*   The `thoughts` field should contain your reasoning in natural language, describing how you interpreted the assertion, what you looked for in the code, and how you arrived at your conclusion.
*   The `result` field is strictly boolean (`true` or `false`).
*   The `explanation` field should only appear if `result` is `false`. Keep the explanation concise but specific, focusing on where and how the code fails to meet the assertion.
*   The output must be valid JSON and adhere strictly to the described schema. Do not include additional fields.
*   Do not mention the reasoning process or chain-of-thought instructions in the `result` or `explanation`; they are for your internal reasoning only.

---

**Examples**

**Positive Example:**

**Input:**

````
[Assertion]
"All methods in {payment_processor} delegate error handling to {error_manager} by wrapping their logic in a context manager."

[Code]
{payment_processor}:
```python
class PaymentProcessor:
    def __init__(self, error_manager):
        self.error_manager = error_manager

    def process_payment(self, amount):
        with self.error_manager.handle_errors('process_payment'):
            return self._run_payment(amount)

    def _run_payment(self, amount):
        # Simulate payment logic
        return True
```

{error_manager}:
```python
from contextlib import contextmanager

class ErrorManager:
    @contextmanager
    def handle_errors(self, operation_name):
        try:
            yield
        except Exception as e:
            # Log or handle error
            raise
```
````

**Output:**

```json
{
  "thoughts": "The assertion requires all methods in PaymentProcessor to delegate error handling to ErrorManager using a context manager. The code shows that the public method process_payment uses with self.error_manager.handle_errors(...). The private method _run_payment is called inside that block, so its errors are also covered. No methods appear to violate this rule. The error_manager class provides a context manager that could handle exceptions. Thus, the assertion is fulfilled.",
  "result": true,
  "explanation": null
}
```

---

**Negative Example:**

**Input:**

````
[Assertion]
"The {user_service} must use {pagination_helper} to paginate all list endpoints, ensuring that requests include a limit and offset."

[Code]
{user_service}:
```python
from flask import Flask, jsonify

app = Flask(__name__)

@app.route('/users', methods=['GET'])
def get_users():
    users = ['Alice', 'Bob', 'Charlie']
    # This endpoint returns all users without pagination
    return jsonify(users)
```

{pagination_helper}:
```python
def paginate(data, limit, offset):
    return data[offset:offset+limit]
```
````

**Output:**

```json
{
  "thoughts": "The assertion states that user_service must use pagination_helper to paginate all list endpoints with limit and offset. The code shows a /users endpoint that returns a full list of users without calling paginate. pagination_helper is defined, but not used. Therefore, the code fails the assertion.",
  "result": false,
  "explanation": "The /users endpoint does not call paginate. It returns all users without applying limit and offset."
}
```
"""


def _format_code_objects(code_objects: List[CodeObject]) -> str:
    """
    Format a list of code objects into a string suitable for LLM evaluation.

    Converts each code object into a markdown-style format with the object's
    name as a header and its code in a Python code block.

    Args:
        code_objects: List of CodeObject instances to format

    Returns:
        A string containing all code objects formatted in markdown style,
        separated by newlines
    """
    formatted_objects: List[str] = []
    for code_object in code_objects:
        source: str = code_object.code
        formatted_objects.append(
            f"""{{{code_object.name}}}:
```python
{source}
```"""
        )
    return "\n".join(formatted_objects)


def _create_evaluation_prompt(expectation: str, code_objects_str: str) -> str:
    """
    Create the main evaluation prompt combining expectation and code.

    Formats the expectation and code objects into a structured prompt that
    follows the system prompt's expected input format.

    Args:
        expectation: The natural language assertion to evaluate
        code_objects_str: Pre-formatted string of code objects

    Returns:
        A formatted string containing the complete evaluation prompt
    """
    return f"""[Assertion]
"{expectation}"

[Code]
{code_objects_str}
"""


class LlamafilePromptFactory(PromptFactory):
    """
    Implementation of PromptFactory for the Llamafile model.

    This class creates prompts specifically formatted for code evaluation using
    the Llamafile model. It combines a detailed system prompt that explains the
    evaluation task with user prompts containing the specific code and
    assertions to evaluate.
    """

    def create_prompt(
        self, expectation: str, code_objects: List[CodeObject]
    ) -> List[Message]:
        logger.debug("Creating prompt for expectation: %s", expectation)
        logger.debug("Number of code objects: %d", len(code_objects))
        """
        Create a complete prompt for code evaluation.

        Generates a list of messages that form a complete conversation prompt
        for the Llamafile model. The prompt includes:
        1. A system message explaining the evaluation task and response format
        2. A user message containing the specific code and assertion to evaluate

        Args:
            expectation: Natural language assertion describing expected code behavior
            code_objects: List of code objects to evaluate

        Returns:
            List of Message objects forming the complete conversation prompt
        """
        code_objects_str = _format_code_objects(code_objects)
        prompt = _create_evaluation_prompt(expectation, code_objects_str)
        logger.debug("Generated evaluation prompt with %d characters", len(prompt))
        messages = [
            Message(
                content=_system_prompt,
                role="system",
            ),
            Message(
                content=prompt,
                role="user",
            ),
        ]
        logger.debug("Created prompt with %d messages", len(messages))
        return messages
