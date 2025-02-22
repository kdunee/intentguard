import json

import jinja2
from datasets import load_dataset

SYSTEM_PROMPT = """You are a code analysis assistant. Your task is to analyze Python code against a natural language assertion and determine if the code fulfills the assertion.

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

INPUT_TEMPLATE = jinja2.Template("""[Assertion]
"{{ assertion }}"

[Code]
{%- for code_object in code_objects %}
{ {{- code_object["name"] -}} }:
```python
{{ code_object["code"] }}
```
{% endfor %}
""")


def generate_output(thoughts, result, explanation):
    output = {
        "thoughts": thoughts,
        "result": result,
        "explanation": explanation,
    }
    return json.dumps(output, indent=2)


def formatting_prompts_func(example):
    assertion = example["assertion"]["assertionText"]
    code_objects = example["codeObjects"]
    thoughts = example["thoughts"]
    explanation = example["explanation"]
    result = explanation is None

    rendered_input = INPUT_TEMPLATE.render(
        assertion=assertion, code_objects=code_objects
    )
    rendered_output = generate_output(thoughts, result, explanation)

    return {
        "instruction": SYSTEM_PROMPT,
        "input": rendered_input,
        "output": rendered_output,
    }


def load_and_map_datasets():
    dataset_train = load_dataset("kdunee/IntentGuard-1", split="train")
    dataset_test = load_dataset("kdunee/IntentGuard-1", split="test")

    dataset_train = dataset_train.map(
        formatting_prompts_func,
        batched=False,
        remove_columns=["assertion", "codeObjects", "thoughts", "explanation"],
    )
    dataset_test = dataset_test.map(
        formatting_prompts_func,
        batched=False,
        remove_columns=["assertion", "codeObjects", "thoughts", "explanation"],
    )
    return dataset_train, dataset_test


def main():
    dataset_train, dataset_test = load_and_map_datasets()
    dataset_train.to_json(
        "data/train.json", lines=False, orient="records", batch_size=1_000_000
    )
    dataset_test.to_json(
        "data/test.json", lines=False, orient="records", batch_size=1_000_000
    )


if __name__ == "__main__":
    main()
