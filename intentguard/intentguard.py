from typing import Dict
import inspect
import json
from collections import Counter

from litellm import completion

from intentguard.intentguard_options import IntentGuardOptions
from intentguard.prompts import system_prompt, reponse_schema


class IntentGuard:
    """
    A class for performing code assertions using Language Models (LLMs).

    This class allows for the evaluation of expectations against provided code objects
    using LLM-based inference. It supports multiple inferences to achieve a quorum
    and provides customizable options for the assertion process.
    """

    def __init__(self, options: IntentGuardOptions = None):
        """
        Initialize the IntentGuard instance.

        Args:
            options (IntentGuardOptions, optional): Configuration options for the assert.
                If not provided, default options will be used.
        """
        if options is None:
            options = IntentGuardOptions()
        self.options = options

    def assert_code(
        self,
        expectation: str,
        params: Dict[str, object],
        options: IntentGuardOptions = None,
    ):
        """
        Perform an assertion using LLM inference.

        This method evaluates the given expectation against the provided parameters
        using LLM-based inference. It performs multiple inferences based on the
        quorum size and determines the final result through voting.

        Args:
            expectation (str): The condition to be evaluated.
            params (Dict[str, object]): A dictionary of objects to be used in the evaluation.
            options (IntentGuardOptions, optional): Custom options for this specific assertion.
                If not provided, the instance's default options will be used.

        Raises:
            AssertionError: If the final result of the assertion is False.
        """
        if options is None:
            options = self.options

        objects_text = self._generate_objects_text(params)
        prompt = self._create_prompt(objects_text, expectation)

        results = []
        for _ in range(options.quorum_size):
            result = self._send_completion_request(prompt, options)
            results.append(result)

        final_result = self._vote_on_results(results)

        if not final_result:
            raise AssertionError(
                f'Expected "{expectation}" to be true, but it was false'
            )

    def _generate_objects_text(self, params: Dict[str, object]) -> str:
        """
        Generate a formatted string representation of the provided objects.

        This method creates a string containing the source code of each object
        in the params dictionary, formatted for use in the LLM prompt.

        Args:
            params (Dict[str, object]): A dictionary of objects to be formatted.

        Returns:
            str: A formatted string containing the source code of all objects.
        """
        objects_texts = []
        for name, obj in params.items():
            source = inspect.getsource(obj)
            object_text = f"""{{{name}}}:
```py
{source}
```
"""
            objects_texts.append(object_text)
        return "\n".join(objects_texts)

    def _create_prompt(self, objects_text: str, expectation: str) -> str:
        """
        Create the prompt for the LLM inference.

        This method combines the formatted objects text and the expectation
        into a single prompt string for the LLM.

        Args:
            objects_text (str): The formatted string of object source codes.
            expectation (str): The condition to be evaluated.

        Returns:
            str: The complete prompt for the LLM inference.
        """
        return f"""**Objects:**
{objects_text}

**Condition:**
"{expectation}"
"""

    def _send_completion_request(
        self, prompt: str, options: IntentGuardOptions
    ) -> bool:
        """
        Send a completion request to the LLM and process the response.

        This method sends the prepared prompt to the LLM using the specified options,
        and processes the response to extract the boolean result.

        Args:
            prompt (str): The prepared prompt for the LLM.
            options (IntentGuardOptions): The options for the LLM request.

        Returns:
            bool: The boolean result of the LLM inference.
        """
        messages = [
            {"content": system_prompt, "role": "system"},
            {"content": prompt, "role": "user"},
        ]

        response = completion(
            model=options.model,
            messages=messages,
            response_format={
                "type": "json_schema",
                "json_schema": reponse_schema,
            },
            temperature=1e-3,
        )
        return json.loads(response.choices[0].message.content)["result"]

    def _vote_on_results(self, results: list) -> bool:
        """
        Determine the final result based on voting.

        This method takes the list of boolean results from multiple LLM inferences
        and determines the final result through a simple majority vote.

        Args:
            results (list): A list of boolean results from multiple LLM inferences.

        Returns:
            bool: The final result based on majority voting.
        """
        vote_count = Counter(results)
        return vote_count[True] > vote_count[False]
