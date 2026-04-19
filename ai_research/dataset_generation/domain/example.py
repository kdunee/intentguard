import re
from dataclasses import dataclass
from typing import Optional

from ai_research.dataset_generation.domain.assertion import Assertion, parse_assertion
from ai_research.dataset_generation.domain.code_object import CodeObject


@dataclass
class Example:
    assertion: Assertion
    code_objects: list[CodeObject]
    thoughts: str
    explanation: Optional[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "assertion": self.assertion.to_dict(),
            "codeObjects": [code_object.to_dict() for code_object in self.code_objects],
            "thoughts": self.thoughts,
            "explanation": self.explanation,
        }


def parse_assertion_text(example_section: str) -> str:
    match = re.search(r"\[Assertion]\s*(?P<assertion>[\w\W]*?)\[Code]", example_section)
    if match is None:
        raise ValueError(f"failed to find assertion in example: {example_section}")
    return match.group("assertion").rstrip(" \t\n\r")


def parse_code_section(example_section: str) -> str:
    match = re.search(r"\[Code]\s*(?P<code>[\w\W]*?)\[Thinking]", example_section)
    if match is None:
        raise ValueError(f"failed to find code section in example: {example_section}")
    return match.group("code").rstrip(" \t\n\r")


def parse_thoughts(example_section: str) -> str:
    match = re.search(
        r"\[Thinking]\s*(?P<thoughts>[\w\W]*?)((\[Explanation])|\Z)",
        example_section,
    )
    if match is None:
        raise ValueError(f"failed to find thoughts in example: {example_section}")
    return match.group("thoughts").rstrip(" \t\n\r")


def parse_explanation(example_section: str) -> Optional[str]:
    match = re.search(r"\[Explanation]\s*(?P<explanation>[\w\W]*)\Z", example_section)
    if match is None:
        return None
    return match.group("explanation").rstrip(" \t\n\r")


def parse_code_objects(code_section: str) -> list[CodeObject]:
    matches = re.finditer(
        r"\{(?P<name>[^}]*)}:\s*```python\s*(?P<code>[\W\w]*?)```",
        code_section,
    )
    return [
        CodeObject(name=match.group("name"), code=match.group("code"))
        for match in matches
    ]


def validate_example(
    assertion: Assertion,
    code_objects: list[CodeObject],
    explanation: Optional[str],
) -> None:
    code_object_names = [code_object.name for code_object in code_objects]
    unique_code_object_names = set(code_object_names)
    if len(unique_code_object_names) != len(code_object_names):
        raise ValueError("duplicate code object definitions found in code section")

    unique_assertion_names = set(assertion.code_object_names)
    if len(unique_assertion_names) != len(code_objects):
        raise ValueError(
            "number of code objects does not match number of code object names in assertion"
        )

    for name in unique_assertion_names:
        if name not in unique_code_object_names:
            raise ValueError(
                f"code object {name} is referenced in assertion but not in code section"
            )

    if explanation is not None:
        lower_explanation = explanation.lower()
        if "example" in lower_explanation or "positive" in lower_explanation:
            raise ValueError(
                "explanation contains forbidden words 'example' or 'positive'"
            )


def parse_example(example_section: str) -> Example:
    assertion_text = parse_assertion_text(example_section)
    assertion = parse_assertion(assertion_text)
    code_section = parse_code_section(example_section)
    thoughts = parse_thoughts(example_section)
    explanation = parse_explanation(example_section)
    code_objects = parse_code_objects(code_section)
    validate_example(assertion, code_objects, explanation)

    return Example(
        assertion=assertion,
        code_objects=code_objects,
        thoughts=thoughts,
        explanation=explanation,
    )
