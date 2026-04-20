import json
import tempfile
import unittest
from argparse import Namespace
from pathlib import Path

import httpx
from openai import BadRequestError

from ai_research.dataset_generation.cli import run_filter, run_generate, run_transform
from ai_research.dataset_generation.domain.assertion import parse_assertion
from ai_research.dataset_generation.domain.example import (
    parse_example,
    parse_assertion_text,
    parse_code_section,
    parse_explanation,
    parse_thoughts,
)
from ai_research.dataset_generation.domain.llm_response import (
    parse_example_sections,
    parse_examples,
)
from ai_research.dataset_generation.infrastructure.openai_client import OpenAITextClient

POSITIVE_EXAMPLE_SECTION = """### Example Set 1: Positive Example (Category: Business Logic)

[Assertion]
"The {OrderProcessor} service uses the {BusinessRulesEngine} to validate and apply business rules for all incoming orders, ensuring that orders comply with the company's policies."

[Code]
{OrderProcessor}:
```python
class OrderProcessor:
    def __init__(self, business_rules_engine):
        self.business_rules_engine = business_rules_engine

    def process_order(self, order):
        if self.business_rules_engine.apply_rules(order):
            print("Order processed successfully.")
        else:
            print("Order failed validation. Cannot proceed.")
```

{BusinessRulesEngine}:
```python
class BusinessRulesEngine:
    def __init__(self):
        self.rules = [self.check_order_value, self.check_customer_credit]

    def apply_rules(self, order):
        for rule in self.rules:
            if not rule(order):
                return False
        return True
```

[Thinking]
- The assertion says the order processor uses the rules engine for validation.
- The code calls `self.business_rules_engine.apply_rules(order)` before processing.
- This aligns with assertion.
"""

NEGATIVE_EXAMPLE_SECTION = """### Example Set 2: Negative Example (Category: Business Logic)

[Assertion]
"The {ProductPricingService} always uses the {PricingStrategy} to determine the final price of products, considering discounts, taxes, and other pricing factors."

[Code]
{ProductPricingService}:
```python
class ProductPricingService:
    def calculate_product_price(self, product):
        base_price = product.base_price
        discount = 0.1
        tax_rate = 0.08
        return base_price * (1 - discount) * (1 + tax_rate)
```

{PricingStrategy}:
```python
from abc import ABC, abstractmethod

class PricingStrategy(ABC):
    @abstractmethod
    def calculate_price(self, product):
        raise NotImplementedError
```

[Thinking]
- Service uses hard-coded pricing.
- Strategy interface exists but service does not call it.

[Explanation]
- The `ProductPricingService` does not use `PricingStrategy`.
- It relies on fixed logic instead.
"""

MULTI_PARAGRAPH_NEGATIVE_EXAMPLE_SECTION = """### Example Set 3: Negative Example (Category: Business Logic)

[Assertion]
"{Service} uses {Validator}."

[Code]
{Service}:
```python
class Service:
    pass
```

{Validator}:
```python
class Validator:
    pass
```

[Thinking]
- Service never calls validator.

[Explanation]
First problem: `Service` does not invoke `Validator`.

Second problem: validation path is missing entirely.

- Missing delegation.
- Missing enforcement.
"""

GENERATE_RESPONSE = """### Example Set 1: Positive Example (Category: Business Logic)

[Assertion]
"{service} uses {helper}."

[Code]
{service}:
```python
class Service:
    pass
```

{helper}:
```python
class Helper:
    pass
```

[Thinking]
- Looks correct.
"""


class _FakeClient:
    def __init__(self, responses):
        self._responses = list(responses)

    def infer(self, template, data):
        del template, data
        return self._responses.pop(0)


class _FakeCompletions:
    def __init__(self, responses):
        self._responses = list(responses)
        self.calls = []

    def create(self, **kwargs):
        self.calls.append(kwargs)
        response = self._responses.pop(0)
        if isinstance(response, Exception):
            raise response
        return response


class _FakeChat:
    def __init__(self, completions):
        self.completions = completions


class _FakeOpenAI:
    def __init__(self, completions):
        self.chat = _FakeChat(completions)


class _FakeMessage:
    def __init__(self, content):
        self.content = content


class _FakeChoice:
    def __init__(self, content):
        self.message = _FakeMessage(content)


class _FakeResponse:
    def __init__(self, content):
        self.choices = [_FakeChoice(content)]


class DatasetGenerationTests(unittest.TestCase):
    def test_parse_assertion_extracts_names(self):
        assertion = parse_assertion(
            '"{user_service} should use dependency injection for {logger} and {database}"'
        )
        self.assertEqual(
            assertion.assertion_text,
            "{user_service} should use dependency injection for {logger} and {database}",
        )
        self.assertEqual(
            assertion.code_object_names,
            ["user_service", "logger", "database"],
        )

    def test_parse_example_sections(self):
        self.assertIn("OrderProcessor", parse_assertion_text(POSITIVE_EXAMPLE_SECTION))
        self.assertIn(
            "BusinessRulesEngine", parse_code_section(POSITIVE_EXAMPLE_SECTION)
        )
        self.assertIn("assertion says", parse_thoughts(POSITIVE_EXAMPLE_SECTION))
        self.assertIsNone(parse_explanation(POSITIVE_EXAMPLE_SECTION))
        self.assertIn("PricingStrategy", parse_explanation(NEGATIVE_EXAMPLE_SECTION))

    def test_parse_explanation_keeps_multiple_paragraphs(self):
        explanation = parse_explanation(MULTI_PARAGRAPH_NEGATIVE_EXAMPLE_SECTION)

        self.assertEqual(
            explanation,
            "First problem: `Service` does not invoke `Validator`.\n\n"
            "Second problem: validation path is missing entirely.\n\n"
            "- Missing delegation.\n"
            "- Missing enforcement.",
        )

    def test_parse_example_allows_duplicate_assertion_references(self):
        example = parse_example(
            """[Assertion]
"{Service} calls {Service} before returning."

[Code]
{Service}:
```python
class Service:
    def run(self):
        return self.run()
```

[Thinking]
- Same code object referenced twice.
"""
        )

        self.assertEqual(
            [code_object.name for code_object in example.code_objects], ["Service"]
        )

    def test_parse_example_rejects_duplicate_code_object_definitions(self):
        with self.assertRaisesRegex(ValueError, "duplicate code object definitions"):
            parse_example(
                """[Assertion]
"{Service} uses {Helper}."

[Code]
{Service}:
```python
class Service:
    pass
```

{Service}:
```python
class Service2:
    pass
```

[Thinking]
- Duplicate code object name.
"""
            )

    def test_parse_example_sections_ignore_headings_inside_fences(self):
        response = """### Example Set 1: Positive Example

[Assertion]
"{Service} uses {Helper}."

[Code]
{Service}:
```python
def run():
    snippet = \"### Example fake heading\"
```

{Helper}:
```python
class Helper:
    pass
```

[Thinking]
- Fine.

### Example Set 2: Negative Example

[Assertion]
"{Other} uses {Helper}."

[Code]
{Other}:
```python
class Other:
    pass
```

{Helper}:
```python
class Helper:
    pass
```

[Thinking]
- Fine.
"""

        sections = parse_example_sections(response)

        self.assertEqual(len(sections), 2)
        self.assertIn('snippet = "### Example fake heading"', sections[0])

    def test_parse_examples_propagates_non_value_error(self):
        from unittest.mock import patch

        with patch(
            "ai_research.dataset_generation.domain.llm_response.parse_example",
            side_effect=RuntimeError("boom"),
        ):
            with self.assertRaisesRegex(RuntimeError, "boom"):
                parse_examples(POSITIVE_EXAMPLE_SECTION)

    def test_run_generate_writes_grouped_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            output_path = Path(tmp_dir) / "output.jsonl"
            args = Namespace(
                api_key="test-key",
                base_url=None,
                model="gpt-4o-mini",
                temperature=1.0,
                max_tokens=1024,
                output=str(output_path),
                count=1,
            )

            run_generate(
                args,
                client_factory=lambda parsed_args: _FakeClient([GENERATE_RESPONSE]),
                category_picker=lambda: "Business Logic",
            )

            rows = output_path.read_text().splitlines()
            self.assertEqual(len(rows), 1)
            payload = json.loads(rows[0])
            self.assertEqual(payload["category"], "Business Logic")
            self.assertEqual(
                payload["examples"][0]["assertion"]["codeObjectNames"],
                ["service", "helper"],
            )

    def test_run_filter_keeps_only_accepted_rows(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "train.jsonl"
            output_path = Path(tmp_dir) / "filtered.jsonl"
            input_path.write_text('{"row": 1}\n{"row": 2}\n')
            args = Namespace(
                api_key="test-key",
                base_url=None,
                model="gpt-4o-mini",
                temperature=1.0,
                max_tokens=1024,
                input=str(input_path),
                output=str(output_path),
            )

            run_filter(
                args,
                client_factory=lambda parsed_args: _FakeClient(
                    [
                        "Verdict: Accept\nReason: good",
                        "Verdict: Reject\nReason: bad",
                    ]
                ),
            )

            self.assertEqual(output_path.read_text(), '{"row": 1}\n')

    def test_run_filter_rejects_acceptable_false_positive(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "train.jsonl"
            output_path = Path(tmp_dir) / "filtered.jsonl"
            input_path.write_text('{"row": 1}\n{"row": 2}\n')
            args = Namespace(
                api_key="test-key",
                base_url=None,
                model="gpt-4o-mini",
                temperature=1.0,
                max_tokens=1024,
                input=str(input_path),
                output=str(output_path),
            )

            run_filter(
                args,
                client_factory=lambda parsed_args: _FakeClient(
                    [
                        "Verdict: Accept\nReason: good",
                        "Verdict: Reject - not acceptable",
                    ]
                ),
            )

            self.assertEqual(output_path.read_text(), '{"row": 1}\n')

    def test_run_transform_flattens_grouped_jsonl(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            input_path = Path(tmp_dir) / "output.jsonl"
            output_path = Path(tmp_dir) / "train.jsonl"
            input_path.write_text(
                json.dumps(
                    {
                        "category": "Business Logic",
                        "examples": [
                            {
                                "assertion": {
                                    "assertionText": "one",
                                    "codeObjectNames": [],
                                }
                            },
                            {
                                "assertion": {
                                    "assertionText": "two",
                                    "codeObjectNames": [],
                                }
                            },
                        ],
                    }
                )
                + "\n"
            )
            args = Namespace(input=str(input_path), output=str(output_path))

            run_transform(args)

            rows = output_path.read_text().splitlines()
            self.assertEqual(len(rows), 2)
            self.assertEqual(json.loads(rows[0])["assertion"]["assertionText"], "one")
            self.assertEqual(json.loads(rows[1])["assertion"]["assertionText"], "two")

    def test_openai_client_retries_with_max_completion_tokens(self):
        client = OpenAITextClient(
            api_key="test-key",
            model="gpt-5-mini",
            temperature=1.0,
            max_tokens=123,
        )
        bad_request = BadRequestError(
            "Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead.",
            response=httpx.Response(
                400,
                request=httpx.Request(
                    "POST", "https://api.openai.com/v1/chat/completions"
                ),
            ),
            body={
                "error": {
                    "message": "Unsupported parameter: 'max_tokens' is not supported with this model. Use 'max_completion_tokens' instead."
                }
            },
        )
        completions = _FakeCompletions([bad_request, _FakeResponse("ok")])
        client._client = _FakeOpenAI(completions)

        result = client.infer("Hello {{.Name}}", {"Name": "world"})

        self.assertEqual(result, "ok")
        self.assertEqual(completions.calls[0]["max_tokens"], 123)
        self.assertNotIn("max_completion_tokens", completions.calls[0])
        self.assertEqual(completions.calls[1]["max_completion_tokens"], 123)
        self.assertNotIn("max_tokens", completions.calls[1])
