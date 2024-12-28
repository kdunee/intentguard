# IntentGuard Training Dataset

This dataset is designed to train models for IntentGuard, a tool that verifies code properties using natural language assertions. It contains examples of Python code paired with natural language assertions describing desired properties of the code.

## Dataset Description

The dataset consists of two files: `train.jsonl` and `test.json`.

*   **`train.jsonl`**: Contains training examples, one per line, in JSON Lines format.
*   **`test.json`**: Contains a list of test examples in JSON format.

Each example includes the following fields:

*   **`assertion`**:
    *   `assertionText`: A natural language assertion describing a positive property of the code.
    *   `codeObjectNames`: A list of strings, each representing the name of a code component referenced in the assertion.
*   **`codeObjects`**: A list of code objects, each with:
    *   `code`: A string containing a Python code snippet.
    *   `name`: A string representing the name of the code component.
*   **`explanation`**: (Only present in negative examples) A string explaining why the code fails to meet the assertion.
*   **`thoughts`**: A string containing a chain-of-thought analysis of the assertion and the code.

The dataset includes both positive examples (where the code satisfies the assertion) and negative examples (where the code fails to satisfy the assertion).

## Intended Use

This dataset is intended for training machine learning models that can understand the relationship between natural language assertions and code behavior. Specifically, it is designed to train models for IntentGuard, a tool that allows developers to express code expectations in natural language.

## Data Format

The dataset is provided in JSON Lines format (`train.jsonl`) and JSON format (`test.json`). Each line in `train.jsonl` is a JSON object representing a single training example. The `test.json` file contains a list of JSON objects, each representing a test example.

## Data Splits

The dataset is split into training and testing sets. The training set is located in `train.jsonl` and the test set is located in `test.json`.
