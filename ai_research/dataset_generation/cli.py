import argparse
import json
import logging
import re
from pathlib import Path
from typing import Callable, Optional, Sequence

from ai_research.dataset_generation.domain.category import get_random_category
from ai_research.dataset_generation.domain.llm_response import parse_examples
from ai_research.dataset_generation.infrastructure.openai_client import OpenAITextClient
from ai_research.dataset_generation.infrastructure.prompts import (
    get_filtering_prompt,
    get_generation_prompt,
)
from ai_research.dataset_generation.infrastructure.storage import (
    write_examples_to_output,
)

logger = logging.getLogger(__name__)


def _add_llm_arguments(parser: argparse.ArgumentParser) -> None:
    parser.add_argument("--model", default="gpt-4o-mini")
    parser.add_argument("--max-tokens", type=int, default=32768)
    parser.add_argument("--temperature", type=float, default=1.0)
    parser.add_argument("--api-key", required=True)
    parser.add_argument("--base-url")


def _build_client(args: argparse.Namespace) -> OpenAITextClient:
    return OpenAITextClient(
        api_key=args.api_key,
        base_url=args.base_url,
        model=args.model,
        temperature=args.temperature,
        max_tokens=args.max_tokens,
    )


def run_generate(
    args: argparse.Namespace,
    client_factory: Callable[[argparse.Namespace], OpenAITextClient] = _build_client,
    category_picker: Callable[[], str] = get_random_category,
) -> int:
    template = get_generation_prompt()
    client = client_factory(args)
    remaining = args.count

    while args.count == 0 or remaining > 0:
        category = category_picker()
        response = client.infer(template, {"Category": category})
        examples = parse_examples(response)
        write_examples_to_output(category, examples, Path(args.output))
        if remaining > 0:
            remaining -= 1

    return 0


def run_filter(
    args: argparse.Namespace,
    client_factory: Callable[[argparse.Namespace], OpenAITextClient] = _build_client,
) -> int:
    template = get_filtering_prompt()
    client = client_factory(args)
    verdict_accept_pattern = re.compile(r"(?im)^verdict:\s*accept\s*$")

    with Path(args.input).open() as in_file, Path(args.output).open("w") as out_file:
        for raw_line in in_file:
            line = raw_line.rstrip("\n")
            if not line:
                continue
            try:
                response = client.infer(template, {"Row": line})
            except Exception:
                logger.exception("Failed to get LLM response")
                continue

            if verdict_accept_pattern.search(response):
                out_file.write(f"{line}\n")

    return 0


def run_transform(args: argparse.Namespace) -> int:
    with Path(args.input).open() as in_file, Path(args.output).open("w") as out_file:
        for raw_line in in_file:
            line = raw_line.strip()
            if not line:
                continue

            output_line = json.loads(line)
            for example in output_line.get("examples", []):
                json.dump(example, out_file)
                out_file.write("\n")

    return 0


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(prog="dataset-generation")
    subparsers = parser.add_subparsers(dest="command", required=True)

    generate_parser = subparsers.add_parser("generate", help="Generate examples")
    _add_llm_arguments(generate_parser)
    generate_parser.add_argument("--output", default="output.jsonl")
    generate_parser.add_argument(
        "--count",
        type=int,
        default=0,
        help="Number of batches to generate. 0 means run forever.",
    )
    generate_parser.set_defaults(func=run_generate)

    filter_parser = subparsers.add_parser("filter", help="Filter dataset examples")
    _add_llm_arguments(filter_parser)
    filter_parser.add_argument("-i", "--input", default="train.jsonl")
    filter_parser.add_argument("-o", "--output", default="filtered.jsonl")
    filter_parser.set_defaults(func=run_filter)

    transform_parser = subparsers.add_parser(
        "transform", help="Transform grouped JSONL into flat JSONL"
    )
    transform_parser.add_argument("-i", "--input", default="output.jsonl")
    transform_parser.add_argument("-o", "--output", default="train.jsonl")
    transform_parser.set_defaults(func=run_transform)

    return parser


def main(argv: Optional[Sequence[str]] = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    logging.basicConfig(level=logging.INFO)
    return args.func(args)
