"""
Logging configuration.

Intended to be called at the start of the application to initialize logging behavior.
"""

import logging


def configure_logging():
    """Configure basic logging."""
    logging.basicConfig(
        level=logging.WARNING, format="%(asctime)s [%(levelname)s] %(message)s"
    )
