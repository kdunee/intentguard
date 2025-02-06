import http.client
import importlib.resources as resources
import json
import logging
import platform
import re
import subprocess
import time
import os
from typing import List, Optional

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


class Llamafile(InferenceProvider):
    """
    Implementation of InferenceProvider using a local Llamafile server.

    This class manages a local Llamafile server instance for performing LLM
    inferences. It handles server startup, communication via HTTP, and response
    parsing. The server uses a quantized GGUF model optimized for code evaluation.

    The server is automatically started when the class is instantiated and
    listens on a dynamically assigned port on localhost. Requests are made
    using the OpenAI-compatible chat completions API.
    """

    def __init__(self):
        """
        Initialize and start the Llamafile server.

        Launches a local Llamafile server process with the configured model and
        waits for it to start accepting connections. The server port is
        automatically detected from the process output.

        Raises:
            Exception: If the server fails to start or if the port cannot be
                detected within the startup timeout period.
        """
        self.process: Optional[subprocess.Popen] = None
        self.temp_dir = None
        self.port = None

        module_resource = resources.files("intentguard").joinpath("infrastructure")
        model_path = str(module_resource.joinpath(MODEL_FILENAME))

        llamafile_path = str(module_resource.joinpath("llamafile.exe"))

        command = [
            llamafile_path,
            "--server",
            "-m",
            model_path,
            "-c",
            str(CONTEXT_SIZE),
            "--host",
            "127.0.0.1",
            "--nobrowser",
        ]

        system = platform.system()
        if system == "Darwin":  # macOS
            # Make llamafile executable on macOS
            try:
                os.chmod(llamafile_path, 0o755)  # rwxr-xr-x
                logger.debug(f"Made llamafile executable at {llamafile_path}")
            except OSError as e:
                logger.warning(f"Failed to make llamafile executable: {e}")

        if system != "Windows":
            # On non-Windows, run in sh
            command.insert(0, "sh")

        self.process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True
        )

        start_time = time.time()
        while time.time() - start_time < STARTUP_TIMEOUT_SECONDS:
            line = self.process.stderr.readline()
            if not line:
                if self.process.poll() is not None:
                    break
                continue
            match = re.search(r"llama server listening at http://127.0.0.1:(\d+)", line)
            if match:
                self.port = int(match.group(1))
                break

        if not self.port:
            status = self.process.poll()
            if status is not None:
                logger.error("Llamafile server failed to start with status %d", status)
                raise Exception(f"llamafile exited with status {status}")
            else:
                logger.error(
                    "Could not detect Llamafile server port within timeout period"
                )
                self.process.kill()
                raise Exception("Could not find port in llamafile output")

        logger.info("Llamafile server started successfully on port %d", self.port)

    def __del__(self):
        """Clean up resources when the instance is destroyed."""
        # Kill the subprocess if it's still running
        if self.process is not None:
            try:
                if self.process.poll() is None:  # process is still running
                    self.process.kill()
                    logger.debug("Killed llamafile server process")
            except Exception as e:
                logger.warning("Failed to kill llamafile server process: %s", e)

    def predict(
        self, prompt: List[Message], inference_options: InferenceOptions
    ) -> Evaluation:
        """
        Generate a prediction using the Llamafile server.

        Makes an HTTP request to the local server's chat completions endpoint,
        formatting the input according to the OpenAI API specification. The
        response is expected to be a JSON object containing a result and
        optional explanation.

        Args:
            prompt: List of messages forming the input prompt
            inference_options: Configuration options for the inference

        Returns:
            An Evaluation object containing the model's assessment

        Raises:
            Exception: If the server returns an error, if the response cannot
                be parsed, or if the request times out
        """
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
            "127.0.0.1", self.port, timeout=INFERENCE_TIMEOUT_SECONDS
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
