import logging
from typing import List

from intentguard.app.message import Message
from intentguard.app.prompt_factory import PromptFactory
from intentguard.domain.code_object import CodeObject
from intentguard.infrastructure.prompt_text import SYSTEM_PROMPT

logger = logging.getLogger(__name__)

_system_prompt = SYSTEM_PROMPT


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
