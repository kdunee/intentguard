import unittest

import intentguard as ig
from intentguard.app.inference_options import InferenceOptions
from intentguard.app.inference_provider import InferenceProvider
from intentguard.app.judgement_cache import JudgementCache
from intentguard.app.message import Message
from intentguard.app.prompt_factory import PromptFactory
from intentguard.domain.code_object import CodeObject
from intentguard.domain.evaluation import Evaluation
from intentguard.domain.judgement_options import JudgementOptions


def sample_subject() -> None:
    pass


class FakeInferenceProvider(InferenceProvider):
    def __init__(self, result: Evaluation) -> None:
        self.result = result
        self.inference_options: list[InferenceOptions] = []

    def predict(
        self, prompt: list[Message], inference_options: InferenceOptions
    ) -> Evaluation:
        self.inference_options.append(inference_options)
        return self.result


class FakePromptFactory(PromptFactory):
    def create_prompt(
        self, expectation: str, code_objects: list[CodeObject]
    ) -> list[Message]:
        return [Message(content=expectation, role="user")]


class NoopJudgementCache(JudgementCache):
    def get(
        self,
        prompt: list[Message],
        inference_options: InferenceOptions,
        judgement_options: JudgementOptions,
    ) -> Evaluation | None:
        return None

    def put(
        self,
        prompt: list[Message],
        inference_options: InferenceOptions,
        judgement_options: JudgementOptions,
        judgement: Evaluation,
    ) -> None:
        pass


class ModuleApiTests(unittest.TestCase):
    def setUp(self) -> None:
        self.original_inference_provider = ig.IntentGuard._inference_provider
        self.original_prompt_factory = ig.IntentGuard._prompt_factory
        self.original_judgement_cache = ig.IntentGuard._judgement_cache_provider
        self.original_default_options = ig.IntentGuard._default_options

        self.provider = FakeInferenceProvider(Evaluation(result=True, explanation=None))
        ig.IntentGuard.set_inference_provider(self.provider)
        ig.IntentGuard.set_prompt_factory(FakePromptFactory())
        ig.IntentGuard.set_judgement_cache_provider(NoopJudgementCache())
        ig.set_default_options(ig.IntentGuardOptions())

    def tearDown(self) -> None:
        ig.IntentGuard.set_inference_provider(self.original_inference_provider)
        ig.IntentGuard.set_prompt_factory(self.original_prompt_factory)
        ig.IntentGuard.set_judgement_cache_provider(self.original_judgement_cache)
        ig.IntentGuard.set_default_options(self.original_default_options)

    def test_module_test_code_returns_evaluation(self) -> None:
        evaluation = ig.test_code("sample should pass", {"subject": sample_subject})

        self.assertIsInstance(evaluation, Evaluation)
        self.assertTrue(evaluation.result)

    def test_module_assert_code_succeeds_when_judgement_is_true(self) -> None:
        ig.assert_code("sample should pass", {"subject": sample_subject})

        self.assertEqual(1, len(self.provider.inference_options))

    def test_module_assert_code_raises_existing_format_when_false(self) -> None:
        self.provider.result = Evaluation(result=False, explanation="sample failed")

        with self.assertRaises(AssertionError) as cm:
            ig.assert_code("sample should pass", {"subject": sample_subject})

        self.assertEqual(
            'Expected "sample should pass" to be true, but it was false.\n'
            "Explanation: sample failed",
            str(cm.exception),
        )

    def test_default_options_affect_module_level_calls(self) -> None:
        ig.set_default_options(
            ig.IntentGuardOptions(num_evaluations=3, temperature=0.2)
        )

        ig.test_code("sample should pass", {"subject": sample_subject})

        self.assertEqual(3, len(self.provider.inference_options))
        self.assertEqual(
            [0.2, 0.2, 0.2],
            [options.temperature for options in self.provider.inference_options],
        )

    def test_per_call_options_override_defaults(self) -> None:
        ig.set_default_options(
            ig.IntentGuardOptions(num_evaluations=3, temperature=0.2)
        )

        ig.test_code(
            "sample should pass",
            {"subject": sample_subject},
            options=ig.IntentGuardOptions(num_evaluations=1, temperature=0.7),
        )

        self.assertEqual(1, len(self.provider.inference_options))
        self.assertEqual(0.7, self.provider.inference_options[0].temperature)

    def test_explicit_instance_options_override_defaults(self) -> None:
        ig.set_default_options(
            ig.IntentGuardOptions(num_evaluations=3, temperature=0.2)
        )
        guard = ig.IntentGuard(
            ig.IntentGuardOptions(num_evaluations=2, temperature=0.6)
        )

        guard.test_code("sample should pass", {"subject": sample_subject})

        self.assertEqual(2, len(self.provider.inference_options))
        self.assertEqual(
            [0.6, 0.6],
            [options.temperature for options in self.provider.inference_options],
        )

    def test_empty_instance_uses_updated_defaults(self) -> None:
        ig.set_default_options(
            ig.IntentGuardOptions(num_evaluations=4, temperature=0.3)
        )
        guard = ig.IntentGuard()

        guard.test_code("sample should pass", {"subject": sample_subject})

        self.assertEqual(4, len(self.provider.inference_options))
        self.assertEqual(
            [0.3, 0.3, 0.3, 0.3],
            [options.temperature for options in self.provider.inference_options],
        )

    def test_options_repr_includes_configured_values(self) -> None:
        options = ig.IntentGuardOptions(num_evaluations=7, temperature=0.1)

        self.assertEqual(
            "IntentGuardOptions(num_evaluations=7, temperature=0.1)",
            repr(options),
        )


if __name__ == "__main__":
    unittest.main()
