import logging

from ai_research.dataset_generation.domain.example import Example, parse_example

logger = logging.getLogger(__name__)


def parse_example_sections(response: str) -> list[str]:
    sections: list[str] = []
    current_section: list[str] | None = None
    in_fence = False

    for line in response.splitlines(keepends=True):
        if line.startswith("```"):
            in_fence = not in_fence

        is_example_heading = (
            not in_fence and line.startswith("### ") and "example" in line.casefold()
        )
        if is_example_heading:
            if current_section:
                sections.append("".join(current_section).strip())
            current_section = []
            continue
        if current_section is not None:
            current_section.append(line)

    if current_section:
        sections.append("".join(current_section).strip())
    return sections


def parse_examples(response: str) -> list[Example]:
    examples: list[Example] = []
    for section in parse_example_sections(response):
        try:
            examples.append(parse_example(section))
        except ValueError as exc:
            logger.warning("Failed to parse example, skipping: %s", exc)
    return examples
