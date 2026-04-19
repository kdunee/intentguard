from typing import List, Optional

from intentguard.app.inference_options import InferenceOptions
from intentguard.app.judgement_cache import JudgementCache
from intentguard.app.message import Message
from intentguard.app.prompt_factory import PromptFactory
from intentguard.domain.code_object import CodeObject
from intentguard.domain.evaluation import Evaluation
from intentguard.domain.judgement_options import JudgementOptions
from intentguard.infrastructure.prompt_text import SYSTEM_PROMPT


class NullJudgementCache(JudgementCache):
    def get(
        self,
        prompt: List[Message],
        inference_options: InferenceOptions,
        judgement_options: JudgementOptions,
    ) -> Optional[Evaluation]:
        return None

    def put(
        self,
        prompt: List[Message],
        inference_options: InferenceOptions,
        judgement_options: JudgementOptions,
        judgement: Evaluation,
    ) -> None:
        return None


class PassthroughPromptFactory(PromptFactory):
    def create_prompt(
        self, expectation: str, code_objects: List[CodeObject]
    ) -> List[Message]:
        del code_objects
        return [
            Message(content=SYSTEM_PROMPT, role="system"),
            Message(content=expectation, role="user"),
        ]
