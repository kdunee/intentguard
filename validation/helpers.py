from typing import List, Optional

from intentguard.app.inference_options import InferenceOptions
from intentguard.app.judgement_cache import JudgementCache
from intentguard.app.message import Message
from intentguard.domain.evaluation import Evaluation
from intentguard.domain.judgement_options import JudgementOptions


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
