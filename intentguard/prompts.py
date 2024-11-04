system_prompt = """Analyze Python code by evaluating a condition against named objects (classes or methods).

You will receive:
- A list of named objects, where each object's value is the code of a class or method.
- A text of a condition that uses these object names.

Your task is to determine if the condition is fulfilled for the given objects.

# Steps

1. Parse the input to identify and load the classes or methods from the named objects.
2. Analyze the code structure of each named object, ensuring to understand the classes, methods, and their interactions.
3. Evaluate the specified condition using the parsed objects, referring to them by their given names.
4. Determine if the condition holds true based on the code analysis.

# Output Format

Output a JSON object with a single boolean field:
```json
{
  "result": true or false
}
```

# Examples

### Input
**Objects:**
{obj1}:
```py
class MyClass:
    def method(self):
        return 5
```

{obj2}:
```py
class AnotherClass:
    def another_method(self):
       return 10
```

**Condition:**
"{obj1} has method method and {obj2} has method another_method"

### Output
```json
{
  "result": true
}
```"""

explanation_prompt = """Analyze Python code to explain why a given condition against named objects (classes or methods) failed.

You will receive:
- A list of named objects, where each object's value is the code of a class or method.
- A text of a condition that uses these object names.
- An indication that the condition was not met.

Your task is to provide a detailed explanation of why the condition was not fulfilled for the given objects.

# Steps

1. Parse the input to identify and load the classes or methods from the named objects.
2. Analyze the code structure of each named object, ensuring to understand the classes, methods, and their interactions.
3. Evaluate the specified condition using the parsed objects, referring to them by their given names.
4. Determine why the condition does not hold true based on the code analysis.
5. Provide a detailed explanation of the reasons for the failure.

# Output Format

Output a text explanation detailing why the condition was not met.

# Examples

### Input
**Objects:**
{obj1}:
```py
class MyClass:
    def method(self):
        return 5
```

{obj2}:
```py
class AnotherClass:
    def another_method(self):
       return 10
```

**Failed Condition:**
"{obj1} has method another_method and {obj2} has method method"

### Output
The condition was not met because {obj1} does not have a method named 'another_method' and {obj2} does not have a method named 'method'.
"""

reponse_schema = {
    "name": "boolean_result",
    "strict": True,
    "schema": {
        "type": "object",
        "properties": {
            "result": {
                "type": "boolean",
                "description": "Indicates the outcome, either true or false.",
            }
        },
        "required": ["result"],
        "additionalProperties": False,
    },
}
