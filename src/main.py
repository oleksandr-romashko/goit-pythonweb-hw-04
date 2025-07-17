"""Entry point for the async CLI file sorter application."""

from __future__ import annotations

import asyncio
import logging
import sys

from aiopath import AsyncPath
from argparse import Namespace
import colorama

from cli.cli import parse_args
from cli.output import print_interrupt_msg
from core.files import validate_source_dir, validate_target_dir
from core.sorter import read_folder, copy_files
from utils.exit_codes import ExitCode
from utils.logger_config import configure_logging, get_console_logger

colorama.init(autoreset=True)

console_logger = get_console_logger()


async def sort_files(source_dir: str, target_dir: str, dry_run: bool = False) -> None:
    """
    Sort files from source directory into structured folders in the target location.

    Args:
        source_dir: Path to the directory with unsorted files.
        target_dir: Path where sorted files will be placed.
        dry_run: Flag for dry-run simulation without actual files copying
    """
    logging.info(
        "[SORTING] Start sorting files with app args: source '%s' and target '%s'.",
        source_dir,
        target_dir,
    )

    # Resolve real paths
    source_dir_path = await AsyncPath(source_dir).resolve()
    target_dir_path = await AsyncPath(target_dir).resolve()
    logging.debug(
        "[SORTING] Source path '%s' resolved: %s", source_dir, source_dir_path
    )
    logging.debug(
        "[SORTING] Target path '%s' resolved: %s", target_dir, target_dir_path
    )

    # Validate paths
    if not await validate_source_dir(source_dir_path, source_dir):
        sys.exit(ExitCode.SOURCE_VALIDATION_ERROR)
    if not await validate_target_dir(target_dir_path, target_dir):
        sys.exit(ExitCode.TARGET_VALIDATION_ERROR)
    logging.debug(
        "[VALIDATION] Source path '%s' and target path '%s' validated successfully.",
        source_dir_path,
        target_dir_path,
    )

    # Scan and categorize files
    mapped_files_dict = await read_folder(source_dir_path)

    # Copy files to structured folders
    await copy_files(mapped_files_dict, target_dir_path, target_dir, dry_run)


async def main() -> None:
    """Main async entry point: parses CLI args and starts sorting."""
    # Parse CLI arguments
    args: Namespace = parse_args()
    source_dir: str = args.source
    target_dir: str = args.target
    debug: bool = args.debug
    dry_run: bool = args.dry_run

    if debug:
        logging.info("[APP] Debug enabled. Enable debug logging to console.")
    if dry_run:
        logging.info(
            "[APP] Dry run enabled. No files will be copied. Simulating sort operation only."
        )

    configure_logging(debug=debug, level=logging.INFO)

    logging.debug("[APP] APPLICATION STARTED.")

    # Call the main app logic
    await sort_files(source_dir, target_dir, dry_run=dry_run)

    logging.debug("[APP] APPLICATION STOPPED.")

# TODO: move some static console prints under console logger, info level, print for dynamic output only
# TODO for enhancements and UX improvements:
# 🔴 Critical: None
# 🟡 Medium Priority:
#    - Add testing, at least for core logic (may require breaking down some function into smaller ones)
#    - Lowering the required version to 3.8+, or even 3.7+ if practical, for wider adoption,
#      like uploading to PyPI, as example:
#       - Replace `import tomllib` with `tomli` (Python <3.11)
#       - Update project metadata in `pyproject.toml` with: requires-python = ">=3.8"
#       - (Optional) Add `__future__` import for annotations: from __future__ import annotations
#       - match-case (pattern matching) - Use if-elif-else (Python Python 3.10+)
#       - Self in annotations - Use quoted class name or workaround (Python 3.11+)
#       - Replace built-in types in annotations (dict, list) with typing.Dict, typing.List, etc.
#         if compatibility with Python 3.8/3.9 is desired for strict linters or type checkers.
#       - walrus operator (:=) minimum required Python version is 3.8
#       - Test backward compatibility on Python 3.8 and 3.9.
#    - Package on PyPI for distribution. Purpose: Broader usage, distribution with
#      global command registration in user system. Purpose: Quality-of-life for frequent users.
# 🟢 Nice to Have:
#    - Add feature: app arg --exclude to ignore certain file types (e.g., .png .js .log)
#      or regexp. Purpose: Control over what to sort (copy) and what to ignore.
#    - Add default values to source improve UX
#      Consider setting default='.' for source (or target) as fallback to current directory.
#    - Adjustable concurrency with number of concurrent coroutines via --concurrency
#      or auto (intelligent adaptation based on number of files, their total size,
#      average size / max size per file).
#      Purpose: For better performance on bigger datasets.
#               Small batches or small files vs larger datasets concurrency
#               may help reduce total time.
#    - Naming strategy for duplicates conflict. Add to the file name text based on parent folder,
#      or move into subfolder.
#      Currently --rename-with-index (default)
#      --rename-with-parent-folder
#      --skip-conflicts
#      --move-duplicates-to /duplicates
#    - Configurable conflict resolution options. Decide what to do when trying to overwrite
#      existing file or fail on first or potential overwrite for most safe execution.
#      Safe overwrite strategies. What to do on first encounter of overwrite.
#      Revoke changes if canceled?
#    - Add feature --show-logfile to print to console content of the application log
#      (user centric, no need to check logs/app.log file - inconvenient)
#      (Caution: may have many lines, so maybe just print last X lines/pages?)
#      Note: currently is solved by --debug arg, but works for current run.
#    - Add feature --verbose - CLI flag like to toggle DEBUG mode dynamically.
# ⬤ Skipped:
#    - Simple progress bar while copying █▒▒▒▒▒▒▒▒▒10%. Helps UX and perception of progress.
#    - tqdm-style (library tqdm.asyncio) progress bar (async-compatible).
#      Slick UX, more detailed than x/y.
if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_interrupt_msg()
        logging.info("[APP] User interrupted execution with Ctrl+C. Exiting app...")
        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        console_logger.error("Unexpected error occurred. Exiting...")
        logging.error("[APP] Unhandled exception: %s", e, exc_info=True)
        sys.exit(ExitCode.GENERAL_ERROR)
