import json
from dataclasses import dataclass
from pathlib import Path

from ai_research.dataset_generation.domain.example import Example


@dataclass
class OutputLine:
    category: str
    examples: list[Example]

    def to_dict(self) -> dict[str, object]:
        return {
            "category": self.category,
            "examples": [example.to_dict() for example in self.examples],
        }


def write_examples_to_output(
    category: str,
    examples: list[Example],
    output_path: Path = Path("output.jsonl"),
) -> None:
    with output_path.open("a") as file:
        json.dump(OutputLine(category=category, examples=examples).to_dict(), file)
        file.write("\n")
