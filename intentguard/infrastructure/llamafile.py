import http.client
import json
import logging
import platform
import subprocess
import time
import os
import hashlib
import urllib.request
from pathlib import Path
from typing import List
import threading
import atexit
import socket

from intentguard.app.inference_options import InferenceOptions
from intentguard.app.inference_provider import InferenceProvider
from intentguard.app.message import Message
from intentguard.domain.evaluation import Evaluation

logger = logging.getLogger(__name__)

# Constants
STARTUP_TIMEOUT_SECONDS = 120  # 2 minutes
INFERENCE_TIMEOUT_SECONDS = 300  # 5 minutes
CONTEXT_SIZE = 32768
MODEL_FILENAME = "IntentGuard-1-qwen2.5-coder-1.5b.gguf"
MODEL_NAME = "IntentGuard-1"
LLAMAFILE_URL = "https://github.com/Mozilla-Ocho/llamafile/releases/download/0.9.0/llamafile-0.9.0"  # URL for llamafile
LLAMAFILE_SHA256 = "5a93cafd16abe61e79761575436339693806385a1f0b7d625024e9f91e71bcf1"  # SHA-256 checksum for llamafile
GGUF_URL = "https://huggingface.co/kdunee/IntentGuard-1-qwen2.5-coder-1.5b-gguf/resolve/main/unsloth.Q4_K_M.gguf"  # URL for the GGUF file
GGUF_SHA256 = "25a0ef913752216890c58fd49d588fa8cc5dde93f669258d29efd8b704cf16c4"  # SHA-256 checksum for the GGUF file
MAX_RETRY_ATTEMPTS = 3  # Maximum number of retries for handling connection errors

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
    logger.info(f"Downloading {url} to {target_path}...")

    # Create parent directories if they don't exist
    target_path.parent.mkdir(parents=True, exist_ok=True)

    # Download the file
    urllib.request.urlretrieve(url, target_path)

    # Verify checksum
    if not verify_checksum(target_path, expected_sha256):
        target_path.unlink()  # Delete the file if checksum verification fails
        raise ValueError(f"Checksum verification failed for {target_path}")

    logger.info(f"Successfully downloaded and verified {target_path}")


def ensure_file(url: str, target_path: Path, expected_sha256: str):
    """Ensure a file exists with the correct checksum."""
    if target_path.exists():
        if verify_checksum(target_path, expected_sha256):
            logger.debug(
                f"{target_path} already exists with correct checksum, skipping download"
            )
            return
        logger.debug(f"{target_path} exists but has incorrect checksum, re-downloading")
        target_path.unlink()
    download_file(url, target_path, expected_sha256)


def get_free_port():
    """
    Dynamically finds a free port on localhost.
    """
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.bind(("localhost", 0))  # Bind to port 0 to let OS choose a free port
    port = sock.getsockname()[1]  # Get the port number assigned by the OS
    sock.close()  # Close the socket (port is still considered occupied temporarily)
    return port


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
            Exception: If the server fails to start, if file downloads
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

            # Get a free port and use it directly
            self._port = get_free_port()

            command = [
                str(llamafile_path),
                "--server",
                "-m",
                str(model_path),
                "-c",
                str(CONTEXT_SIZE),
                "--host",
                "127.0.0.1",
                "--port",
                str(self._port),
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

            # Start the process with stdout/stderr redirected to devnull
            self._process = subprocess.Popen(
                command, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL
            )

            # Give the server a moment to start
            start_time = time.time()
            while time.time() - start_time < STARTUP_TIMEOUT_SECONDS:
                # Check if the process is still running
                if self._process.poll() is not None:
                    status = self._process.poll()
                    logger.error(
                        "Llamafile server failed to start with status %d", status
                    )
                    raise Exception(f"llamafile exited with status {status}")

                # Try to connect to the server to verify it's ready
                try:
                    with socket.create_connection(("127.0.0.1", self._port), timeout=1):
                        logger.info(
                            "Llamafile server started successfully on port %d",
                            self._port,
                        )
                        return
                except (socket.timeout, ConnectionRefusedError):
                    # Wait a bit before trying again
                    time.sleep(1)

            # If we get here, the server didn't start within the timeout
            self._process.kill()
            self._process = None
            self._port = None
            raise Exception(
                f"Llamafile server failed to start within {STARTUP_TIMEOUT_SECONDS} seconds"
            )

    def _send_http_request(self, payload: dict) -> dict:
        """
        Sends an HTTP request to the Llamafile server with the given payload
        and returns the parsed JSON response.
        """
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
        if not json_response.get("choices"):
            error_msg = f"Llamafile API returned no choices: {json_response}"
            logger.error(error_msg)
            raise Exception(error_msg)
        return json_response

    def predict(
        self, prompt: List[Message], inference_options: InferenceOptions
    ) -> Evaluation:
        """
        Generate a prediction using the Llamafile server.

        If a timeout occurs, the method will retry up to MAX_RETRY_ATTEMPTS times,
        restarting the server process between attempts.
        """
        messages = [{"role": m.role, "content": m.content} for m in prompt]
        payload = {
            "model": MODEL_NAME,
            "messages": messages,
            "temperature": inference_options.temperature,
        }

        attempts = 0
        last_error = None

        while attempts < MAX_RETRY_ATTEMPTS:
            attempts += 1
            try:
                self._ensure_process()
                logger.debug(
                    f"Attempt {attempts}/{MAX_RETRY_ATTEMPTS}: Preparing prediction request with temperature {inference_options.temperature:.2f}"
                )

                json_response = self._send_http_request(payload)
                generated_text = json_response["choices"][0]["message"]["content"]
                if generated_text.endswith("<|eot_id|>"):
                    generated_text = generated_text[: -len("<|eot_id|>")]

                # Fix common JSON parsing issues
                generated_text = (
                    generated_text.replace('"""', '\\"\\"\\"')
                    .replace('\\\\"\\"\\"', '\\"\\"\\"')
                    .replace('\\\\"', '\\"')
                    .replace('["', '[\\"')
                    .replace('"]', '\\"]')
                )

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

            except (
                socket.timeout,
                TimeoutError,
                ConnectionRefusedError,
                ConnectionError,
                http.client.HTTPException,
            ) as e:
                last_error = e
                logger.warning(
                    f"Error occurred during attempt {attempts}/{MAX_RETRY_ATTEMPTS}: {e}"
                )
                if attempts < MAX_RETRY_ATTEMPTS:
                    logger.info("Restarting llamafile process and retrying...")
                    self.shutdown()  # Kill the existing process
                else:
                    logger.error(
                        f"Failed after {MAX_RETRY_ATTEMPTS} attempts due to timeouts"
                    )
                    raise Exception(
                        f"Llamafile request failed after {MAX_RETRY_ATTEMPTS} attempts"
                    ) from last_error
            except Exception as e:
                logger.error(f"Error during prediction: {e}")
                raise

        raise Exception(
            f"Llamafile request failed after {MAX_RETRY_ATTEMPTS} attempts"
        ) from last_error
