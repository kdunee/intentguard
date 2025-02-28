import json
import logging

from tqdm import tqdm
import intentguard as ig
from datasets import load_dataset
from intentguard.app.message import Message
from intentguard.infrastructure.llamafile_prompt_factory import _system_prompt

logger = logging.getLogger(__name__)


def load_test_dataset():
    return load_dataset("kdunee/IntentGuard-1-alpaca-format", split="test")


def monkey_patch_intentguard():
    # - Disable caching
    # - Provide the entire prompt throught the `expectation` argument
    def patched_get(*args, **kwargs):
        return None

    ig.IntentGuard._judgement_cache_provider.get = patched_get

    def patched_create_prompt(expectation, *args, **kwargs):
        messages = [
            Message(
                content=_system_prompt,
                role="system",
            ),
            Message(
                content=expectation,
                role="user",
            ),
        ]
        return messages

    ig.IntentGuard._prompt_factory.create_prompt = patched_create_prompt


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
    monkey_patch_intentguard()
    validate_model()
