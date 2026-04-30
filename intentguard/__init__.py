from intentguard.app.intentguard import IntentGuard
from intentguard.app.intentguard_options import IntentGuardOptions
from intentguard.domain.evaluation import Evaluation as _Evaluation
from intentguard.infrastructure.fs_judgement_cache import FsJudgementCache
from intentguard.infrastructure.llamafile import Llamafile
from intentguard.infrastructure.llamafile_prompt_factory import LlamafilePromptFactory

judgement_cache = FsJudgementCache()
IntentGuard.set_judgement_cache_provider(judgement_cache)

llamafile = Llamafile()
IntentGuard.set_inference_provider(llamafile)

prompt_factory = LlamafilePromptFactory()
IntentGuard.set_prompt_factory(prompt_factory)


def test_code(
    expectation: str,
    params: dict[str, object],
    options: IntentGuardOptions | None = None,
) -> _Evaluation:
    return IntentGuard().test_code(expectation, params, options)


def assert_code(
    expectation: str,
    params: dict[str, object],
    options: IntentGuardOptions | None = None,
) -> None:
    IntentGuard().assert_code(expectation, params, options)


def set_default_options(options: IntentGuardOptions) -> None:
    IntentGuard.set_default_options(options)


__all__ = [
    "IntentGuard",
    "IntentGuardOptions",
    "assert_code",
    "set_default_options",
    "test_code",
]
