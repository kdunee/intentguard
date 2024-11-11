"""
This module implements a caching system for IntentGuard results to avoid redundant API calls.
It stores results in JSON files within a .intentguard directory, using SHA-256 hashes as cache keys.
"""

import os
import hashlib
import json
from typing import Optional, Dict, Any
from intentguard.intentguard_options import IntentGuardOptions

# Directory where cache files will be stored
CACHE_DIR = ".intentguard"


def ensure_cache_dir_exists() -> None:
    """
    Creates the cache directory if it doesn't exist.
    This is called before any cache operations to ensure the cache directory is available.
    """
    if not os.path.exists(CACHE_DIR):
        os.makedirs(CACHE_DIR)


def generate_cache_key(
    expectation: str, objects_text: str, options: IntentGuardOptions
) -> str:
    """
    Generates a unique cache key based on the input parameters and model configuration.

    The key includes a version prefix ('v1') to allow for cache invalidation if the
    caching logic changes in future versions of the software. This ensures old cached
    results won't be used if they're incompatible with newer versions.

    Args:
        expectation (str): The expectation string being tested
        objects_text (str): The text of the objects being analyzed
        options: Configuration object containing model and evaluation settings

    Returns:
        str: A SHA-256 hash that serves as the cache key
    """
    key_string = (
        f"v1:{expectation}:{objects_text}:{options.model}:{options.num_evaluations}"
    )
    return hashlib.sha256(key_string.encode()).hexdigest()


def read_cache(cache_key: str) -> Optional[Dict[str, Any]]:
    """
    Retrieves cached results for a given cache key.

    Args:
        cache_key (str): The SHA-256 hash key to look up

    Returns:
        dict: The cached result if found, None otherwise
    """
    ensure_cache_dir_exists()
    cache_file = os.path.join(CACHE_DIR, cache_key)
    if os.path.exists(cache_file):
        with open(cache_file, "r") as f:
            return json.load(f)
    return None


def write_cache(cache_key: str, result: Dict[str, Any]) -> None:
    """
    Stores a result in the cache using the provided cache key.

    Args:
        cache_key (str): The SHA-256 hash key to store the result under
        result: The data to cache (must be JSON serializable)
    """
    ensure_cache_dir_exists()
    cache_file = os.path.join(CACHE_DIR, cache_key)
    with open(cache_file, "w") as f:
        json.dump(result, f)


class CachedResult:
    """
    Represents a cached IntentGuard verification result.

    This class provides a structured way to store and serialize verification results,
    including both the boolean outcome and any explanation text.
    """

    def __init__(self, result: bool, explanation: str = ""):
        """
        Initialize a new CachedResult instance.

        Args:
            result (bool): The verification result (True/False)
            explanation (str, optional): Explanation of the result. Defaults to empty string.
        """
        self.result = result
        self.explanation = explanation

    def to_dict(self) -> Dict[str, Any]:
        """
        Converts the CachedResult instance to a dictionary for JSON serialization.

        Returns:
            dict: Dictionary containing the result and explanation
        """
        return {"result": self.result, "explanation": self.explanation}

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CachedResult":
        """
        Creates a CachedResult instance from a dictionary.

        Args:
            data (dict): Dictionary containing 'result' and optionally 'explanation'

        Returns:
            CachedResult: A new CachedResult instance
        """
        return cls(result=data["result"], explanation=data.get("explanation", ""))
