import http.client
import json
import logging
import platform
import re
import subprocess
import time
import os
import hashlib
import urllib.request
from pathlib import Path
from typing import List
import threading
import atexit

from intentguard.app.inference_options import InferenceOptions
from intentguard.app.inference_provider import InferenceProvider
from intentguard.app.message import Message
from intentguard.domain.evaluation import Evaluation

logger = logging.getLogger(__name__)

# Constants
STARTUP_TIMEOUT_SECONDS = 120  # 2 minutes
INFERENCE_TIMEOUT_SECONDS = 300  # 5 minutes
CONTEXT_SIZE = 8192
MODEL_FILENAME = "IntentGuard-1.Q8_0.gguf"
MODEL_NAME = "IntentGuard-1"
LLAMAFILE_URL = "https://github.com/Mozilla-Ocho/llamafile/releases/download/0.8.17/llamafile-0.8.17"  # URL for llamafile
LLAMAFILE_SHA256 = "1041e05b2c254674e03c66052b1a6cf646e8b15ebd29a195c77fed92cac60d6b"  # SHA-256 checksum for llamafile
GGUF_URL = "https://huggingface.co/kdunee/IntentGuard-1/resolve/main/IntentGuard-1.Q8_0.gguf"  # URL for the GGUF file
GGUF_SHA256 = "0cb9476a129e7fc68b419ab86397b9ce4309b0d5faf6ba5d18629e796ca01383"  # SHA-256 checksum for the GGUF file

STORAGE_DIR = Path(".intentguard")


def compute_checksum(file_path: Path) -> str:
    """Compute the SHA-256 checksum of a file."""
    sha256_hash = hashlib.sha256()
    with open(file_path, "rb") as f:
        for byte_block in iter(lambda: f.read(4096), b""):
            sha256_hash.update(byte_block)
    return sha256_hash.hexdigest()


def verify_checksum(file_path: Path, expected_sha256: str) -> bool:
    """Verify the SHA-256 checksum of a file."""
    return compute_checksum(file_path) == expected_sha256


def download_file(url: str, target_path: Path, expected_sha256: str):
    """Download a file and verify its checksum."""
    print(f"Downloading {url} to {target_path}...")

    # Create parent directories if they don't exist
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Download the file
    urllib.request.urlretrieve(url, target_path)

    # Verify checksum
    if not verify_checksum(target_path, expected_sha256):
        target_path.unlink()  # Delete the file if checksum verification fails
        raise ValueError(f"Checksum verification failed for {target_path}")

    print(f"Successfully downloaded and verified {target_path}")


def ensure_file(url: str, target_path: Path, expected_sha256: str):
    """Ensure a file exists with the correct checksum."""
    if target_path.exists():
        if verify_checksum(target_path, expected_sha256):
            print(
                f"{target_path} already exists with correct checksum, skipping download"
            )
            return
        print(f"{target_path} exists but has incorrect checksum, re-downloading")
        target_path.unlink()
    download_file(url, target_path, expected_sha256)


class Llamafile(InferenceProvider):
    """
    Implementation of InferenceProvider using a local Llamafile server.

    This class manages a local Llamafile server instance for performing LLM
    inferences. It handles server startup, communication via HTTP, and response
    parsing. The server uses a quantized GGUF model optimized for code evaluation.

    The server is lazily initialized when the first inference is requested,
    and listens on a dynamically assigned port on localhost. Requests are made
    using the OpenAI-compatible chat completions API.

    The GGUF model weights and server binary are downloaded on-demand when the
    first inference is requested, if they are not already present in the
    infrastructure directory.
    """

    def __init__(self):
        """
        Initialize the Llamafile provider.

        The actual server process and required files are initialized lazily
        when the first prediction is requested. This constructor only sets up
        the basic instance attributes and threading lock.
        """
        self._process = None
        self._port = None
        self._process_lock = threading.Lock()
        atexit.register(self.shutdown)

    def shutdown(self):
        """Shutdown the Llamafile server process in a thread-safe manner."""
        with self._process_lock:
            if self._process is not None:
                try:
                    if self._process.poll() is None:  # process is still running
                        self._process.kill()
                        logger.debug("Killed llamafile server process")
                except Exception as e:
                    logger.warning("Failed to kill llamafile server process: %s", e)
                self._process = None
                self._port = None

    def _ensure_process(self):
        """
        Ensure the Llamafile server process is running.

        Downloads required files if not present and starts the server process
        if it hasn't been started yet. This method is thread-safe and handles
        concurrent initialization attempts.

        Raises:
            Exception: If the server fails to start, if the port cannot be
                detected within the startup timeout period, or if file downloads
                or verification fail.
        """
        if self._process is not None:
            return

        with self._process_lock:
            if self._process is not None:
                return

            model_path = STORAGE_DIR.joinpath(MODEL_FILENAME)
            llamafile_path = STORAGE_DIR.joinpath("llamafile.exe")

            ensure_file(LLAMAFILE_URL, llamafile_path, LLAMAFILE_SHA256)
            ensure_file(GGUF_URL, model_path, GGUF_SHA256)

            command = [
                str(llamafile_path),
                "--server",
                "-m",
                str(model_path),
                "-c",
                str(CONTEXT_SIZE),
                "--host",
                "127.0.0.1",
                "--nobrowser",
            ]

            system = platform.system()
            if system != "Windows":
                try:
                    os.chmod(str(llamafile_path), 0o755)
                    logger.debug(f"Made llamafile executable at {llamafile_path}")
                except OSError as e:
                    logger.warning(f"Failed to make llamafile executable: {e}")
                command.insert(0, "sh")

            self._process = subprocess.Popen(
                command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
            )

            start_time = time.time()
            while time.time() - start_time < STARTUP_TIMEOUT_SECONDS:
                line = self._process.stderr.readline()
                if not line:
                    if self._process.poll() is not None:
                        break
                    continue
                match = re.search(
                    r"llama server listening at http://127.0.0.1:(\d+)", line
                )
                if match:
                    self._port = int(match.group(1))
                    break

            if not self._port:
                status = self._process.poll()
                if status is not None:
                    logger.error(
                        "Llamafile server failed to start with status %d", status
                    )
                    raise Exception(f"llamafile exited with status {status}")
                else:
                    logger.error(
                        "Could not detect Llamafile server port within timeout period"
                    )
                    self._process.kill()
                    raise Exception("Could not find port in llamafile output")

            logger.info("Llamafile server started successfully on port %d", self._port)

    def predict(
        self, prompt: List[Message], inference_options: InferenceOptions
    ) -> Evaluation:
        """
        Generate a prediction using the Llamafile server.

        Ensures the server is running (starting it if necessary) and makes an HTTP
        request to the local server's chat completions endpoint, formatting the
        input according to the OpenAI API specification. The response is expected
        to be a JSON object containing a result and optional explanation.

        Args:
            prompt: List of messages forming the input prompt
            inference_options: Configuration options for the inference

        Returns:
            An Evaluation object containing the model's assessment

        Raises:
            Exception: If the server fails to start, returns an error, if the
                response cannot be parsed, or if the request times out
        """
        self._ensure_process()
        logger.debug(
            "Preparing prediction request with temperature %.2f",
            inference_options.temperature,
        )
        messages = [{"role": m.role, "content": m.content} for m in prompt]
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": inference_options.temperature,
        }

        conn = http.client.HTTPConnection(
            "127.0.0.1", self._port, timeout=INFERENCE_TIMEOUT_SECONDS
        )
        try:
            conn.request(
                "POST",
                "/v1/chat/completions",
                body=json.dumps(payload),
                headers={"Content-Type": "application/json"},
            )
            response = conn.getresponse()
            data = response.read()
        finally:
            conn.close()

        if response.status != 200:
            error_msg = f"Llamafile API error: {response.status} {response.reason} {data.decode()}"
            logger.error(error_msg)
            raise Exception(error_msg)

        json_response = json.loads(data)

        if not json_response["choices"]:
            error_msg = f"Llamafile API returned no choices: {json_response}"
            logger.error(error_msg)
            raise Exception(error_msg)

        generated_text = json_response["choices"][0]["message"]["content"]
        if generated_text.endswith("<|eot_id|>"):
            generated_text = generated_text[: -len("<|eot_id|>")]

        try:
            llm_response = json.loads(generated_text)

            return Evaluation(
                result=llm_response["result"],
                explanation=llm_response["explanation"],
            )
        except json.JSONDecodeError as e:
            error_msg = f"Could not parse Llamafile response: {generated_text}"
            logger.error(error_msg)
            raise Exception(error_msg) from e
