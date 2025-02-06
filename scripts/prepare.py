import sys
import hashlib
import urllib.request
from pathlib import Path

INFRASTRUCTURE_DIR = Path(__file__).parent.parent / "intentguard" / "infrastructure"

LLAMAFILE_URL = "https://github.com/Mozilla-Ocho/llamafile/releases/download/0.8.17/llamafile-0.8.17"  # URL for llamafile
LLAMAFILE_SHA256 = "1041e05b2c254674e03c66052b1a6cf646e8b15ebd29a195c77fed92cac60d6b"  # SHA-256 checksum for llamafile


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


def main():
    """Main entry point for the prepare script."""
    try:
        # Download llamafile.exe
        llamafile_path = INFRASTRUCTURE_DIR / "llamafile.exe"
        ensure_file(LLAMAFILE_URL, llamafile_path, LLAMAFILE_SHA256)

    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
