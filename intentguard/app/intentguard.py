import logging
from typing import Optional, Dict

from intentguard.app.inference_options import InferenceOptions
from intentguard.app.inference_provider import InferenceProvider
from intentguard.app.intentguard_options import IntentGuardOptions
from intentguard.app.judgement_cache import JudgementCache
from intentguard.app.prompt_factory import PromptFactory
from intentguard.domain.code_object import CodeObject
from intentguard.domain.evaluation import Evaluation
from intentguard.domain.judge import Judge
from intentguard.domain.judgement_options import JudgementOptions

logger = logging.getLogger(__name__)


class IntentGuard:
    """
    A class for performing code assertions using Language Models (LLMs).

    This class evaluates expectations against provided code objects using LLM-based inference.
    It supports multiple inferences to achieve a consensus through voting and provides
    customizable options for the assertion process.
    """

    _inference_provider: InferenceProvider
    _prompt_factory: PromptFactory
    _judgement_cache_provider: JudgementCache

    @classmethod
    def set_inference_provider(cls, inference_provider: InferenceProvider) -> None:
        """
        Set the inference provider for LLM-based evaluations.

        Args:
            inference_provider: Provider implementation for LLM inference
        """
        logger.info(
            "Setting inference provider: %s", inference_provider.__class__.__name__
        )
        cls._inference_provider = inference_provider

    @classmethod
    def set_prompt_factory(cls, prompt_factory: PromptFactory) -> None:
        """
        Set the prompt factory for generating LLM evaluation prompts.

        Args:
            prompt_factory: Factory implementation for creating prompts
        """
        logger.info("Setting prompt factory: %s", prompt_factory.__class__.__name__)
        cls._prompt_factory = prompt_factory

    @classmethod
    def set_judgement_cache_provider(
        cls, judgement_cache_provider: JudgementCache
    ) -> None:
        """
        Set the cache provider for storing evaluation results.

        Args:
            judgement_cache_provider: Provider implementation for caching judgements
        """
        logger.info(
            "Setting judgement cache provider: %s",
            judgement_cache_provider.__class__.__name__,
        )
        cls._judgement_cache_provider = judgement_cache_provider

    def __init__(self, options: Optional[IntentGuardOptions] = None) -> None:
        """
        Initialize the IntentGuard instance.

        Args:
            options: Configuration options for assertions. Uses default options if None.
        """
        self.options: IntentGuardOptions = options or IntentGuardOptions()
        logger.debug("Initialized IntentGuard with options: %s", self.options)

    def test_code(
        self,
        expectation: str,
        params: Dict[str, object],
        options: Optional[IntentGuardOptions] = None,
    ) -> Evaluation:
        """
        Test if code meets an expected condition using LLM inference.

        Performs multiple LLM inferences and uses a judge to determine consensus on whether
        the code meets the specified expectation. Results are cached for performance.

        Args:
            expectation: The condition to evaluate, expressed in natural language
            params: Dictionary mapping variable names to code objects for evaluation
            options: Custom options for this test, falls back to instance defaults

        Returns:
            Evaluation object containing the test result and explanation
        """
        options = options or self.options
        inference_options = InferenceOptions(temperature=options.temperature)
        judgement_options = JudgementOptions()

        code_objects = CodeObject.from_dict(params)
        prompt = IntentGuard._prompt_factory.create_prompt(expectation, code_objects)

        logger.debug("Testing code with expectation: %s", expectation)
        logger.debug("Code objects: %s", code_objects)

        cached_judgement = IntentGuard._judgement_cache_provider.get(
            prompt, inference_options, judgement_options
        )
        if cached_judgement:
            logger.info("Using cached judgement for prompt")
            return cached_judgement

        logger.info("Performing %d evaluations", options.num_evaluations)
        evaluations = []
        for i in range(options.num_evaluations):
            logger.debug("Running evaluation %d/%d", i + 1, options.num_evaluations)
            evaluation = IntentGuard._inference_provider.predict(
                prompt, inference_options
            )
            evaluations.append(evaluation)
        judge = Judge(judgement_options)
        logger.debug("Making final judgement from %d evaluations", len(evaluations))
        judgement = judge.make_judgement(evaluations)

        logger.debug("Caching judgement result")
        IntentGuard._judgement_cache_provider.put(
            prompt, inference_options, judgement_options, judgement
        )

        return judgement

    def assert_code(
        self,
        expectation: str,
        params: Dict[str, object],
        options: Optional[IntentGuardOptions] = None,
    ) -> None:
        """
        Assert that code meets an expected condition using LLM inference.

        Similar to test_code(), but raises an AssertionError if the evaluation fails.
        This method is designed for use in test suites and validation scenarios.

        Args:
            expectation: The condition to evaluate, expressed in natural language
            params: Dictionary mapping variable names to code objects for evaluation
            options: Custom options for this assertion, falls back to instance defaults

        Raises:
            AssertionError: If the code does not meet the expected condition
        """
        logger.info("Asserting code meets expectation: %s", expectation)
        evaluation = self.test_code(expectation, params, options)
        if not evaluation.result:
            logger.warning("Assertion failed: %s", expectation)
            raise AssertionError(
                f'Expected "{expectation}" to be true, but it was false.\n'
                f"Explanation: {evaluation.explanation}"
            )
