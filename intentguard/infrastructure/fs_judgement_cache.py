import hashlib
import json
import logging
from pathlib import Path
from typing import List, Optional

from intentguard.app.inference_options import InferenceOptions
from intentguard.app.judgement_cache import JudgementCache
from intentguard.app.message import Message
from intentguard.domain.evaluation import Evaluation
from intentguard.domain.judgement_options import JudgementOptions

logger = logging.getLogger(__name__)


class FsJudgementCache(JudgementCache):
    """
    File system-based implementation of the JudgementCache interface.

    This class provides a persistent cache for evaluation results using the local
    file system. Each cache entry is stored in a separate file, with the filename
    derived from a hash of the input parameters. Cache files are stored in a
    '.intentguard' directory in the current working directory.
    """

    def __init__(self):
        self.cache_dir = Path(".intentguard")
        logger.debug("Initialized cache directory at %s", self.cache_dir)

    def _get_cache_file_path(
        self,
        prompt: List[Message],
        inference_options: InferenceOptions,
        judgement_options: JudgementOptions,
    ) -> Path:
        """
        Generate a unique file path for caching an evaluation result.

        Creates a deterministic file path by hashing the combination of prompt,
        inference options, and judgement options. This ensures that identical
        evaluation requests map to the same cache file.

        Args:
            prompt: The list of messages forming the evaluation prompt
            inference_options: Configuration for the inference process
            judgement_options: Configuration for the judgement process

        Returns:
            Path object pointing to the cache file location
        """
        input_str = f"v2:{prompt}:{inference_options}:{judgement_options}"
        hashed_input = hashlib.sha256(input_str.encode()).hexdigest()
        return self.cache_dir / hashed_input

    def get(
        self,
        prompt: List[Message],
        inference_options: InferenceOptions,
        judgement_options: JudgementOptions,
    ) -> Optional[Evaluation]:
        """
        Retrieve a cached evaluation result if available.

        Attempts to load and deserialize a cached evaluation result from the file
        system. Returns None if the cache file doesn't exist or if there are any
        errors reading or parsing the file.

        Args:
            prompt: The list of messages forming the evaluation prompt
            inference_options: Configuration for the inference process
            judgement_options: Configuration for the judgement process

        Returns:
            The cached Evaluation if found and valid, None otherwise
        """
        file_path = self._get_cache_file_path(
            prompt, inference_options, judgement_options
        )
        if not file_path.exists():
            logger.debug("Cache miss for %s", file_path)
            return None
        try:
            with open(file_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                logger.debug("Cache hit for %s", file_path)
                return Evaluation(**data)
        except Exception as e:
            logger.warning("Failed to read cache file %s: %s", file_path, str(e))
            return None

    def put(
        self,
        prompt: List[Message],
        inference_options: InferenceOptions,
        judgement_options: JudgementOptions,
        judgement: Evaluation,
    ):
        """
        Store an evaluation result in the cache.

        Serializes and writes the evaluation result to a file in the cache
        directory. Creates the cache directory if it doesn't exist.

        Args:
            prompt: The list of messages forming the evaluation prompt
            inference_options: Configuration for the inference process
            judgement_options: Configuration for the judgement process
            judgement: The evaluation result to cache
        """
        file_path = self._get_cache_file_path(
            prompt, inference_options, judgement_options
        )
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        try:
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(judgement.__dict__, f)
            logger.debug("Successfully cached judgement at %s", file_path)
        except Exception as e:
            logger.error("Failed to write cache file %s: %s", file_path, str(e))
