from dataclasses import dataclass
from typing import Optional


@dataclass
class Evaluation:
    """
    A class representing the result of an LLM-based code evaluation.

    This class encapsulates the outcome of evaluating code against specified
    expectations using a language model. It includes both a boolean result
    indicating success or failure, and an optional explanation providing
    context or reasoning for the evaluation outcome.

    Attributes:
        result: Boolean indicating whether the code meets the specified expectations
        explanation: Optional string providing reasoning or details about the evaluation.
            This can include:
            - Why the code meets or fails to meet expectations
            - Specific issues identified in the code
            - Suggestions for improvement
            May be None if no explanation is provided
    """

    result: bool
    explanation: Optional[str]
