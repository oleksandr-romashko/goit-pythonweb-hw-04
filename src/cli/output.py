"""Handles formatted CLI output for file processing tasks.

Includes functions for printing progress updates, summaries, and user feedback
such as spinners, status messages, and error notices. Designed for an enhanced
terminal user experience with color and emoji indicators.
"""

import time

from colorama import Style

from utils.logger_config import get_console_logger


console_logger = get_console_logger()


def get_spinner_dots(start_time: float, spinner: list[str] | None = None) -> str:
    """Returns the current spinner frame based on elapsed time.

    Args:
        start_time (float): The monotonic start time to calculate elapsed duration.
        spinner (list[str], optional): A list of frames to use for the spinner.

    Returns:
        str: The current frame in the spinner animation, padded for alignment.
    """
    default_spinner = [".", "..", "...", "...."]
    frames_per_sec = 2  # 2 times per second, e.g. update frame each 0.5 seconds
    spinner = spinner or default_spinner

    elapsed = time.monotonic() - start_time

    current_frame = spinner[int(elapsed * frames_per_sec) % len(spinner)]

    return f"{current_frame:<{max(len(frame) for frame in spinner)}}"


def print_line(
    message: str = "", end: str = "\n", overwrite_prev: bool = False
) -> None:
    """Prints a line to the console, optionally overwriting the previous one.

    Args:
        message (str): The message to print.
        end (str): The end character (defaults to newline).
        overwrite_prev (bool): If True, overwrites the current line in the terminal.
    """
    prefix = "\r" if overwrite_prev else ""
    print(f"{prefix}{message}", end=end, flush=True)


def print_mapping_update(found_counter: int, start_time: float) -> None:
    """Prints a dynamic update showing how many files were found so far.

    Args:
        found_counter (int): The number of files found.
        start_time (float): The start time for calculating spinner frame.
    """
    spinner_frame = get_spinner_dots(start_time)
    print_line(
        f"🔎 Found {Style.BRIGHT}{found_counter} files{Style.RESET_ALL} so far{spinner_frame}",
        overwrite_prev=True,
        end="",
    )


def print_mapping_summary(
    files_map: dict[str, list[dict]],
    time_to_execute: float,
    skipped_count: int = 0,
):
    """Prints a summary of the file mapping and analysis process.

    Includes grouped counts per extension, duplicates, conflicts, and size stats.

    Args:
        files_map (dict): Mapping of file extensions to lists of file info dictionaries.
        time_to_execute (float): Total execution time in seconds.
        skipped_count (int, optional): Number of files skipped due to errors.
    """
    total_files = 0
    total_duplicates = 0
    total_conflicts = 0
    total_bytes_to_copy = 0

    time_to_execute_str = f"{time_to_execute:.2f}s"

    print_line("📁 Files grouped by extension:", overwrite_prev=True)
    for extension, entries in sorted(files_map.items()):
        ext_total = len(entries)
        ext_duplicates = 0
        ext_conflicts = 0

        # Keep newest files first (latest modified file as the one to keep if duplicate)
        sorted_entries_by_newest = sorted(
            entries, key=lambda f: f["modified"], reverse=True
        )
        for file_info in sorted_entries_by_newest:
            output_name = file_info.get("output_name")
            if output_name is None:  # Duplicate
                ext_duplicates += 1
            elif output_name != file_info["name"]:  # Conflict
                ext_conflicts += 1
                total_bytes_to_copy += file_info["size"]
            else:
                total_bytes_to_copy += file_info["size"]

        duplicates_str = (
            f"{ext_duplicates} duplicate" + ("s" if ext_duplicates != 1 else "")
            if ext_duplicates
            else ""
        )
        conflicts_str = (
            f"{ext_conflicts} conflict{("s" if ext_conflicts != 1 else "")} resolved"
            if ext_conflicts
            else ""
        )

        per_ext_summary = ", ".join(filter(None, [duplicates_str, conflicts_str]))
        per_ext_summary_str = f" ({per_ext_summary})" if per_ext_summary else ""

        print_line(
            f"  {extension.ljust(12)} {ext_total} files{per_ext_summary_str}",
        )

        total_files += ext_total
        total_duplicates += ext_duplicates
        total_conflicts += ext_conflicts

    # Extra empty line
    print_line("")

    # Skipped files
    if skipped_count:
        console_logger.warning(
            "Skipped %d file%s due to unreadable format or permission issues",
            skipped_count,
            "s" if skipped_count != 1 else "",
        )

    # Final summary
    extras = []
    if total_duplicates:
        extras.append(
            f"{total_duplicates} duplicate{'s' if total_duplicates != 1 else ''} to skip"
        )
    if total_conflicts:
        extras.append(
            f"{total_conflicts} conflict{'s' if total_conflicts != 1 else ''} resolved"
        )

    extras_str = f" ({', '.join(extras)})" if extras else ""
    print_line(
        f"✅ Found {Style.BRIGHT}{total_files} files{Style.RESET_ALL} "
        f"in {time_to_execute_str}{extras_str}",
    )

    # Size to copy
    if total_bytes_to_copy > 0:
        total_mb = total_bytes_to_copy / (1024 * 1024)
        print_line(f"📦 Estimated total to copy: {total_mb:.2f} MB")

    # Extra empty line
    print_line("")


def print_copy_update(copied_counter: int, total_files: int, start_time: float):
    """Prints a dynamic update showing the number of files copied so far.

    Args:
        copied_counter (int): Number of files successfully copied.
        total_files (int): Total number of files to copy.
        start_time (float): The start time for calculating spinner frame.
    """
    spinner_frame = get_spinner_dots(start_time)
    print_line(
        (
            f"📄 Copied {Style.BRIGHT}{copied_counter}{Style.RESET_ALL}/{Style.BRIGHT}{total_files} "
            f"files{Style.RESET_ALL}{spinner_frame}"
        ),
        overwrite_prev=True,
        end="",
    )


def print_copy_summary(
    files_number: int, origin_path: str, time_to_execute: float, error_count: int = 0
):
    """Prints a final summary after the file copy operation is completed.

    Args:
        files_number (int): Total number of files copied.
        origin_path (str): Destination directory path.
        time_to_execute (float): Duration of the copy operation.
        error_count (int, optional): Number of copy failures.
    """
    time_to_execute_str = f"{time_to_execute:.2f}s"
    errors_str = f"\n⚠️  Failed to copy {error_count} files" if error_count else ""
    print_line(
        (
            f"✅ Copied {Style.BRIGHT}{files_number} files{Style.RESET_ALL} "
            f"into '{Style.BRIGHT}{origin_path}{Style.RESET_ALL}' folder "
            f"in {time_to_execute_str}"
            f"{errors_str}"
        ),
        overwrite_prev=True,
    )


def print_interrupt_msg():
    """Prints a message indicating that execution was interrupted."""
    print_line()
    console_logger.warning(
        "Execution interrupted. Sorting was cancelled before completion."
    )
