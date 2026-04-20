import subprocess
import tarfile
import tempfile
import unittest
import zipfile
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]


class PackagingTests(unittest.TestCase):
    def test_build_artifacts_keep_dev_code_out(self):
        with tempfile.TemporaryDirectory() as tmp_dir:
            subprocess.run(
                ["uv", "build", "--out-dir", tmp_dir],
                check=True,
                cwd=ROOT,
                capture_output=True,
                text=True,
            )

            wheel_path = next(Path(tmp_dir).glob("*.whl"))
            with zipfile.ZipFile(wheel_path) as wheel:
                wheel_names = wheel.namelist()

            self.assertFalse(
                any(name.startswith("validation/") for name in wheel_names)
            )
            self.assertFalse(
                any(name.startswith("ai_research/") for name in wheel_names)
            )
            self.assertFalse(any(name.startswith("tests/") for name in wheel_names))
            self.assertTrue(
                any(name.startswith("intentguard/") for name in wheel_names)
            )

            sdist_path = next(Path(tmp_dir).glob("*.tar.gz"))
            with tarfile.open(sdist_path, "r:gz") as sdist:
                sdist_names = sdist.getnames()

            self.assertFalse(any("/validation/" in name for name in sdist_names))
            self.assertFalse(any("/ai_research/" in name for name in sdist_names))
            self.assertFalse(any("/tests/" in name for name in sdist_names))
