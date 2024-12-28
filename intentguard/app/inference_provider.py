from abc import ABC, abstractmethod
from typing import List

from intentguard.app.inference_options import InferenceOptions
from intentguard.app.message import Message
from intentguard.domain.evaluation import Evaluation


class InferenceProvider(ABC):
    """
    Abstract base class defining the interface for Language Model inference providers.

    This class serves as a contract for implementing different LLM backends that can
    perform code evaluations. Implementations of this class handle the actual interaction
    with specific language models (e.g., LLaMA, GPT) to generate evaluations based on
    provided prompts.
    """

    @abstractmethod
    def predict(
        self, prompt: List[Message], inference_options: InferenceOptions
    ) -> Evaluation:
        """
        Generate an evaluation prediction using the language model.

        Args:
            prompt: A list of messages forming the input prompt for the model
            inference_options: Configuration options for controlling inference behavior

        Returns:
            An Evaluation object containing the model's assessment and explanation

        Note:
            Implementations should handle any necessary prompt formatting, model
            interaction, and response parsing specific to their LLM backend.
        """
        pass
