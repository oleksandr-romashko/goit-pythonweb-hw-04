"""Exit codes for CLI application.

Defines standard exit codes to indicate different termination reasons.
"""

from __future__ import annotations

from enum import IntEnum

class ExitCode(IntEnum):
    """Standard exit codes used across the CLI application."""

    SUCCESS = 0
    SOURCE_VALIDATION_ERROR = 1
    TARGET_VALIDATION_ERROR = 2
    GENERAL_ERROR = 10
