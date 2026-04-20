import json
import logging

from datasets import load_dataset
from tqdm import tqdm

import intentguard as ig
from validation.helpers import NullJudgementCache, PassthroughPromptFactory

logger = logging.getLogger(__name__)


def load_test_dataset():
    return load_dataset("kdunee/IntentGuard-1-alpaca-format", split="test")


def configure_validation_intentguard() -> None:
    ig.IntentGuard.set_judgement_cache_provider(NullJudgementCache())
    ig.IntentGuard.set_prompt_factory(PassthroughPromptFactory())


def validate_model():
    dataset = load_test_dataset()

    options = ig.IntentGuardOptions(num_evaluations=3, temperature=0.4)
    guard = ig.IntentGuard(options)

    y_gt = []
    y_pred = []
    for example in tqdm(dataset):
        try:
            inp = example.get("input")
            expected_result = json.loads(example.get("output"))["result"]
            results = []
            for _ in range(5):
                result = guard.test_code(inp, {}).result
                results.append(result)
            final_result = all(results)
            y_gt.append(
                not expected_result
            )  # The dataset is inverted, we're looking for negative examples
            y_pred.append(not final_result)
            logger.info(f"Expected: {expected_result}, Got: {final_result}")
        except Exception:
            logger.exception("Error while processing example")

    accuracy = sum([1 for gt, pred in zip(y_gt, y_pred) if gt == pred]) / len(y_gt)
    precision = (
        sum([1 for gt, pred in zip(y_gt, y_pred) if gt == pred and gt]) / sum(y_pred)
        if sum(y_pred)
        else 0
    )
    recall = (
        sum([1 for gt, pred in zip(y_gt, y_pred) if gt == pred and gt]) / sum(y_gt)
        if sum(y_gt)
        else 0
    )

    logger.info(f"Accuracy: {accuracy}")
    logger.info(f"Precision: {precision}")
    logger.info(f"Recall: {recall}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    configure_validation_intentguard()
    validate_model()
