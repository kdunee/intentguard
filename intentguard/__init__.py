from intentguard.app.intentguard import IntentGuard
from intentguard.app.intentguard_options import IntentGuardOptions
from intentguard.infrastructure.fs_judgement_cache import FsJudgementCache
from intentguard.infrastructure.llamafile import Llamafile
from intentguard.infrastructure.llamafile_prompt_factory import LlamafilePromptFactory

judgement_cache = FsJudgementCache()
IntentGuard.set_judgement_cache_provider(judgement_cache)

llamafile = Llamafile()
IntentGuard.set_inference_provider(llamafile)

prompt_factory = LlamafilePromptFactory()
IntentGuard.set_prompt_factory(prompt_factory)

__all__ = ["IntentGuard", "IntentGuardOptions"]
