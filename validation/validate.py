import linecache
import logging
import types
from typing import Any, Dict, Optional

from datasets import load_dataset
from tqdm import tqdm

import intentguard as ig
from validation.helpers import NullJudgementCache

logger = logging.getLogger(__name__)


def load_test_dataset():
    return load_dataset("kdunee/IntentGuard-1", split="test")


def configure_validation_intentguard() -> None:
    ig.IntentGuard.set_judgement_cache_provider(NullJudgementCache())


def _build_synthetic_module(
    name: str, code: str, example_index: int, code_index: int
) -> types.ModuleType:
    safe_name = "".join(
        char if char.isalnum() or char in "._-" else "_" for char in name
    )
    source = code if code.endswith("\n") else f"{code}\n"
    filename = f"/intentguard_validation/example_{example_index:06d}_{code_index:02d}_{safe_name}.py"

    # Seed linecache so inspect.getsource() can recover dataset snippets.
    linecache.cache[filename] = (
        len(source),
        None,
        source.splitlines(keepends=True),
        filename,
    )

    module = types.ModuleType(name)
    module.__file__ = filename
    return module


def _build_validation_params(
    example: Dict[str, Any], example_index: int
) -> Dict[str, object]:
    params: Dict[str, object] = {}
    for code_index, code_object in enumerate(example["codeObjects"]):
        params[code_object["name"]] = _build_synthetic_module(
            name=code_object["name"],
            code=code_object["code"],
            example_index=example_index,
            code_index=code_index,
        )
    return params


def validate_model(max_examples: Optional[int] = None):
    dataset = load_test_dataset()
    total_examples = (
        min(len(dataset), max_examples) if max_examples is not None else len(dataset)
    )

    options = ig.IntentGuardOptions(num_evaluations=3, temperature=0.4)
    guard = ig.IntentGuard(options)

    y_true = []
    y_pred = []
    for example_index, example in enumerate(tqdm(dataset, total=total_examples)):
        if max_examples is not None and example_index >= max_examples:
            break

        try:
            expectation = example["assertion"]["assertionText"]
            params = _build_validation_params(example, example_index)
            expected_result = example["explanation"] is None
            results = []
            for _ in range(5):
                result = guard.test_code(expectation, params).result
                results.append(result)
            final_result = all(results)
            y_true.append(expected_result)
            y_pred.append(final_result)
            logger.info(f"Expected: {expected_result}, Got: {final_result}")
        except Exception:
            logger.exception("Error while processing example %d", example_index)

    if not y_true:
        raise ValueError("Validation did not process any examples")

    true_positives = sum(1 for gt, pred in zip(y_true, y_pred) if gt and pred)
    predicted_positives = sum(y_pred)
    actual_positives = sum(y_true)

    accuracy = sum(1 for gt, pred in zip(y_true, y_pred) if gt == pred) / len(y_true)
    precision = true_positives / predicted_positives if predicted_positives else 0
    recall = true_positives / actual_positives if actual_positives else 0

    logger.info(f"Processed examples: {len(y_true)}")
    logger.info(f"Accuracy: {accuracy}")
    logger.info(f"Precision: {precision}")
    logger.info(f"Recall: {recall}")


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO)
    configure_validation_intentguard()
    validate_model()
