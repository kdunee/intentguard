import logging
import os


def configure_test_logging() -> None:
    """Configure deterministic, timestamped logging for test runs."""
    configured_level = os.getenv("INTENTGUARD_TEST_LOG_LEVEL", "INFO").upper()
    level = getattr(logging, configured_level, logging.INFO)
    logging.basicConfig(
        level=level,
        format="%(asctime)s %(levelname)s %(name)s - %(message)s",
        force=True,
    )
