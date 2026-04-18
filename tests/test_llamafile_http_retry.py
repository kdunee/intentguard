import json
import unittest
from typing import ClassVar
from unittest.mock import patch

from intentguard.infrastructure.llamafile import Llamafile
from tests.logging_config import configure_test_logging


configure_test_logging()


class _FakeResponse:
    def __init__(self, status: int, reason: str, body: dict):
        self.status = status
        self.reason = reason
        self._body = json.dumps(body).encode("utf-8")

    def read(self) -> bytes:
        return self._body


class _FakeHTTPConnection:
    responses: ClassVar[list[_FakeResponse]] = []

    def __init__(self, *_args, **_kwargs):
        self._response = None

    def request(self, *_args, **_kwargs):
        self._response = self.responses.pop(0)

    def getresponse(self):
        return self._response

    def close(self):
        return None


class TestLlamafileHttpRetry(unittest.TestCase):
    def test_retries_when_model_is_loading(self):
        _FakeHTTPConnection.responses = [
            _FakeResponse(
                503,
                "Service Unavailable",
                {"error": {"message": "Loading model", "code": 503}},
            ),
            _FakeResponse(
                200,
                "OK",
                {"choices": [{"message": {"content": "ok"}}]},
            ),
        ]

        provider = Llamafile()
        provider._port = 12345

        with (
            patch(
                "intentguard.infrastructure.llamafile.http.client.HTTPConnection",
                _FakeHTTPConnection,
            ),
            patch("intentguard.infrastructure.llamafile.time.sleep", return_value=None),
        ):
            response = provider._send_http_request({"messages": []})

        self.assertEqual(response["choices"][0]["message"]["content"], "ok")


if __name__ == "__main__":
    unittest.main()
