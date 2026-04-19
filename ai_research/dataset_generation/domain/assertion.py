import re
from dataclasses import dataclass


@dataclass
class Assertion:
    assertion_text: str
    code_object_names: list[str]

    def to_dict(self) -> dict[str, object]:
        return {
            "assertionText": self.assertion_text,
            "codeObjectNames": self.code_object_names,
        }


def parse_assertion(assertion_text: str) -> Assertion:
    matches = re.findall(r"\{([^}]*)}", assertion_text)
    return Assertion(
        assertion_text=assertion_text.strip('"'),
        code_object_names=matches,
    )
