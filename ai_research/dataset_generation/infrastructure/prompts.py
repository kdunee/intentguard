from pathlib import Path

_DATA_DIR = Path(__file__).resolve().parent.parent / "data"


def get_generation_prompt() -> str:
    return (_DATA_DIR / "prompt.txt").read_text()


def get_filtering_prompt() -> str:
    return (_DATA_DIR / "filtering.txt").read_text()
