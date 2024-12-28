from collections import Counter
import logging
from typing import List

from intentguard.domain.evaluation import Evaluation
from intentguard.domain.judgement_options import JudgementOptions

logger = logging.getLogger(__name__)


class Judge:
    """
    A class for making final judgements based on multiple LLM evaluations.

    This class implements a voting mechanism to aggregate multiple evaluations
    into a single consensus result. It uses majority voting to determine the
    final outcome and provides explanatory context for negative results.
    """

    def __init__(self, judgement_options: JudgementOptions):
        """
        Initialize the Judge with configuration options.

        Args:
            judgement_options: Configuration options for the judgement process
        """
        self.judgement_options = judgement_options

    def make_judgement(self, evaluations: List[Evaluation]) -> Evaluation:
        """
        Aggregate multiple evaluations into a final judgement using majority voting.

        This method counts positive and negative evaluations to determine the
        consensus. For negative results, it includes an explanation from the first
        failing evaluation that provides one.

        Args:
            evaluations: List of individual Evaluation objects to aggregate

        Returns:
            A single Evaluation representing the consensus judgement.
            The result is True if there are more positive than negative votes.
            For negative results, includes an explanation from a failing evaluation.
        """
        vote_count = Counter(evaluation.result for evaluation in evaluations)
        final_result = vote_count[True] > vote_count[False]

        logger.info(
            "Vote count - Positive: %d, Negative: %d",
            vote_count[True],
            vote_count[False],
        )

        explanation = None
        if not final_result:
            logger.debug("Finding explanation for negative judgement")
            for evaluation in evaluations:
                if not evaluation.result and evaluation.explanation:
                    explanation = evaluation.explanation
                    logger.debug("Using explanation: %s", explanation)
                    break

        logger.info("Final judgement: %s", "Pass" if final_result else "Fail")
        return Evaluation(result=final_result, explanation=explanation)
