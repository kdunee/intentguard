from typing import Dict, List, Any, Optional, cast
import inspect
import json
from collections import Counter
from dataclasses import dataclass

from litellm import completion
from litellm.main import ModelResponse
from litellm.types.utils import Choices

from intentguard.intentguard_options import IntentGuardOptions
from intentguard.prompts import system_prompt, reponse_schema, explanation_prompt
from intentguard.cache import generate_cache_key, read_cache, write_cache, CachedResult


@dataclass
class LLMRequest:
    """Configuration for an LLM API request"""

    messages: List[Dict[str, str]]
    model: str
    temperature: float = 1e-3
    response_format: Optional[Dict[str, Any]] = None


class IntentGuard:
    """
    A class for performing code assertions using Language Models (LLMs).

    This class evaluates expectations against provided code objects using LLM-based inference.
    It supports multiple inferences to achieve a consensus through voting and provides
    customizable options for the assertion process.
    """

    def __init__(self, options: Optional[IntentGuardOptions] = None) -> None:
        """
        Initialize the IntentGuard instance.

        Args:
            options: Configuration options for assertions. Uses default options if None.
        """
        self.options: IntentGuardOptions = options or IntentGuardOptions()

    def assert_code(
        self,
        expectation: str,
        params: Dict[str, object],
        options: Optional[IntentGuardOptions] = None,
    ) -> None:
        """
        Assert that code meets an expected condition using LLM inference.

        Performs multiple LLM inferences and uses majority voting to determine if the
        code meets the specified expectation. Results are cached for performance.

        Args:
            expectation: The condition to evaluate, expressed in natural language
            params: Dictionary mapping variable names to code objects for evaluation
            options: Custom options for this assertion, falls back to instance defaults

        Raises:
            AssertionError: If the code does not meet the expected condition
        """
        options = options or self.options

        # Prepare evaluation context
        objects_text: str = self._format_code_objects(params)
        prompt: str = self._create_evaluation_prompt(objects_text, expectation)
        cache_key: str = generate_cache_key(expectation, objects_text, options)

        # Check cache or perform evaluation
        final_result: CachedResult = self._get_cached_or_evaluate(
            cache_key=cache_key, prompt=prompt, options=options
        )

        # Handle failed assertions
        if not final_result.result:
            raise AssertionError(
                f'Expected "{expectation}" to be true, but it was false.\n'
                f"Explanation: {final_result.explanation}"
            )

    def _format_code_objects(self, params: Dict[str, Any]) -> str:
        """
        Format code objects for LLM evaluation.

        Extracts and formats the source code of each object in the params dictionary.

        Args:
            params: Dictionary of named code objects

        Returns:
            Formatted string containing source code of all objects
        """
        formatted_objects: List[str] = []
        for name, obj in params.items():
            source: str = inspect.getsource(obj)
            formatted_objects.append(
                f"""{{{name}}}:
```py
{source}
```"""
            )
        return "\n".join(formatted_objects)

    def _create_evaluation_prompt(self, objects_text: str, expectation: str) -> str:
        """
        Create the complete prompt for LLM evaluation.

        Args:
            objects_text: Formatted source code of objects to evaluate
            expectation: The condition to evaluate

        Returns:
            Complete prompt string for LLM
        """
        return f"""**Objects:**
{objects_text}

**Condition:**
"{expectation}"
"""

    def _get_cached_or_evaluate(
        self, cache_key: str, prompt: str, options: IntentGuardOptions
    ) -> CachedResult:
        """
        Retrieve cached result or perform new evaluation.

        Args:
            cache_key: Key for cache lookup
            prompt: Evaluation prompt if cache miss
            options: Configuration options for evaluation

        Returns:
            Evaluation result, either from cache or newly computed
        """
        if cached_result := read_cache(cache_key):
            return CachedResult.from_dict(cached_result)

        # Perform multiple evaluations for consensus
        results: List[bool] = [
            self._perform_single_evaluation(prompt, options)
            for _ in range(options.num_evaluations)
        ]

        final_result: CachedResult = CachedResult(
            result=self._determine_consensus(results)
        )

        # Generate explanation for failed assertions
        if not final_result.result:
            final_result.explanation = self._generate_failure_explanation(
                prompt, options
            )

        write_cache(cache_key, final_result.to_dict())
        return final_result

    def _perform_single_evaluation(
        self, prompt: str, options: IntentGuardOptions
    ) -> bool:
        """
        Perform a single LLM evaluation.

        Args:
            prompt: The evaluation prompt
            options: Configuration options

        Returns:
            Boolean result of evaluation
        """
        request: LLMRequest = LLMRequest(
            messages=[
                {"content": system_prompt, "role": "system"},
                {"content": prompt, "role": "user"},
            ],
            model=options.model,
            response_format={
                "type": "json_schema",
                "json_schema": reponse_schema,
            },
        )

        response: ModelResponse = self._send_llm_request(request)
        return json.loads(
            cast(str, cast(Choices, response.choices[0]).message.content)
        )["result"]

    def _generate_failure_explanation(
        self, prompt: str, options: IntentGuardOptions
    ) -> str:
        """
        Generate explanation for failed assertion.

        Args:
            prompt: The evaluation prompt
            options: Configuration options

        Returns:
            Detailed explanation of why assertion failed
        """
        request: LLMRequest = LLMRequest(
            messages=[
                {"content": explanation_prompt, "role": "system"},
                {"content": prompt, "role": "user"},
            ],
            model=options.model,
        )

        response: ModelResponse = self._send_llm_request(request)
        return cast(str, cast(Choices, response.choices[0]).message.content)

    def _send_llm_request(self, request: LLMRequest) -> ModelResponse:
        """
        Send request to LLM API.

        Args:
            request: Configuration for the API request

        Returns:
            API response
        """
        return completion(
            model=request.model,
            messages=request.messages,
            temperature=request.temperature,
            response_format=request.response_format,
        )

    def _determine_consensus(self, results: List[bool]) -> bool:
        """
        Determine final result through majority voting.

        Args:
            results: List of boolean results from multiple evaluations

        Returns:
            Consensus result
        """
        vote_count: Counter = Counter(results)
        return vote_count[True] > vote_count[False]
