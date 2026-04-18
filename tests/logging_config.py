import logging


def configure_test_logging() -> None:
    """Configure deterministic, timestamped logging for test runs."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        force=True,
    )
