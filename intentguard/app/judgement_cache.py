from abc import ABC, abstractmethod
from typing import Optional, List

from intentguard.app.inference_options import InferenceOptions
from intentguard.app.message import Message
from intentguard.domain.evaluation import Evaluation
from intentguard.domain.judgement_options import JudgementOptions


class JudgementCache(ABC):
    """
    Abstract base class defining the interface for caching evaluation judgements.

    This class serves as a contract for implementing caching mechanisms to store and
    retrieve LLM evaluation results. Caching helps improve performance by avoiding
    redundant model inferences for previously evaluated prompts.
    """

    @abstractmethod
    def get(
        self,
        prompt: List[Message],
        inference_options: InferenceOptions,
        judgement_options: JudgementOptions,
    ) -> Optional[Evaluation]:
        """
        Retrieve a cached evaluation result if available.

        Args:
            prompt: The list of messages forming the evaluation prompt
            inference_options: The inference configuration used for the evaluation
            judgement_options: The judgement configuration used for the evaluation

        Returns:
            The cached Evaluation if found, None otherwise

        Note:
            Implementations should use all three parameters (prompt, inference_options,
            and judgement_options) as part of the cache key to ensure cached results
            are only returned for identical evaluation conditions.
        """
        pass

    @abstractmethod
    def put(
        self,
        prompt: List[Message],
        inference_options: InferenceOptions,
        judgement_options: JudgementOptions,
        judgement: Evaluation,
    ):
        """
        Store an evaluation result in the cache.

        Args:
            prompt: The list of messages forming the evaluation prompt
            inference_options: The inference configuration used for the evaluation
            judgement_options: The judgement configuration used for the evaluation
            judgement: The evaluation result to cache

        Note:
            Implementations should handle cache invalidation strategies and storage
            mechanisms appropriate for their use case (e.g., in-memory, file-system,
            distributed cache).
        """
        pass
