from abc import ABC, abstractmethod
from typing import List

from intentguard.app.message import Message
from intentguard.domain.code_object import CodeObject


class PromptFactory(ABC):
    """
    Abstract base class for creating structured prompts for LLM evaluation.

    This class serves as a contract for implementing prompt generation strategies
    that combine code objects with natural language expectations. The generated
    prompts are used to guide language models in evaluating code against specified
    criteria.
    """

    @abstractmethod
    def create_prompt(
        self, expectation: str, code_objects: List[CodeObject]
    ) -> List[Message]:
        """
        Create a structured prompt for LLM evaluation.

        Args:
            expectation: Natural language description of the expected code behavior
                or properties to evaluate
            code_objects: List of code objects to evaluate against the expectation

        Returns:
            A list of Message objects forming the complete evaluation prompt,
            typically including system context, code content, and the evaluation
            task

        Note:
            Implementations should structure the prompt to effectively guide the
            LLM in performing accurate code evaluation, potentially including:
            - Clear evaluation criteria
            - Relevant code context
            - Expected response format
        """
        pass
