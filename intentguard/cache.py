import os
import hashlib
import json

CACHE_DIR = ".intentguard"


def ensure_cache_dir_exists():
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def generate_cache_key(expectation: str, objects_text: str, options) -> str:
    key_string = f"{expectation}:{objects_text}:{options.model}:{options.quorum_size}"
    return hashlib.sha256(key_string.encode()).hexdigest()


def read_cache(cache_key: str):
    ensure_cache_dir_exists()
    cache_file = os.path.join(CACHE_DIR, cache_key)
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)
    return None


def write_cache(cache_key: str, result):
    ensure_cache_dir_exists()
    cache_file = os.path.join(CACHE_DIR, cache_key)
    with open(cache_file, "w") as f:
        json.dump(result, f)


class CachedResult:
    def __init__(self, result: bool, explanation: str = ""):
        self.result = result
        self.explanation = explanation

    def to_dict(self):
        return {"result": self.result, "explanation": self.explanation}

    @classmethod
    def from_dict(cls, data: dict):
        return cls(result=data["result"], explanation=data.get("explanation", ""))
