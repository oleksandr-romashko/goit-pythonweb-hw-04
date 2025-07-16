"""
Core logic for file sorting and copying.

This module provides functionality to:
- Recursively scan a directory and group files by extension.
- Generate SHA-256 hashes for uniqueness checks.
- Resolve filename duplicates and conflicts.
- Copy files to a target directory while preserving uniqueness.
- Provide real-time CLI and logging feedback.
"""

import asyncio
from collections import defaultdict
import logging
import time

from aiopath import AsyncPath  # type: ignore

from core.files import (
    get_file_extension,
    copy_file,
)
from cli.output import (
    print_mapping_update,
    print_mapping_summary,
    print_copy_update,
    print_dry_run_msg,
    print_copy_summary,
)
from utils.hash_calculator import get_file_hash


async def read_folder(
    source_path: AsyncPath,
) -> dict[str, list[dict]]:
    """
    Recursively walk through the source directory and group all files by their extension.

    Returns a mapping of extensions to lists of AsyncPath file objects.
    """
    logging.info("[READ] Start reading source folder content at: %s", source_path)

    # Start tracking execution time
    start_time = time.monotonic()

    files_map: dict[str, list[dict]] = defaultdict(list)
    found_counter = 0
    skipped_counter = 0

    async def walk_dir(path: AsyncPath):
        nonlocal found_counter, skipped_counter

        async for entry in path.iterdir():
            try:
                if await entry.is_file():
                    # await asyncio.sleep(0.05)  # simulate delay
                    ext = get_file_extension(entry) or "no_extension"
                    stat = await entry.stat()
                    size = stat.st_size
                    hash_sum = await get_file_hash(entry)
                    modified = stat.st_mtime  # UNIX timestamp
                    file_info = {
                        "path": entry,
                        "name": entry.name,
                        "size": size,
                        "hash": hash_sum,
                        "modified": modified,
                    }
                    files_map[ext].append(file_info)
                    found_counter += 1
                    print_mapping_update(found_counter, start_time)
                elif await entry.is_dir():
                    await walk_dir(entry)
            except OSError as exc:
                skipped_counter += 1
                logging.warning(
                    "[READ] ❌ Error occurred while reading '%s': %s. Skipped unreadable entry.",
                    entry,
                    exc,
                )

    # Perform source directory file mapping, incl. all subdirectories
    logging.info("[READ] Analyzing and mapping files in folder: %s", source_path)
    await walk_dir(source_path)

    # Resolve duplicate and conflicting file names
    files_map = resolve_duplicates_and_conflicts(files_map)

    # Calculate total operation time
    elapsed_time = time.monotonic() - start_time

    # Show summary
    print_mapping_summary(files_map, elapsed_time, skipped_counter)
    logging.info(
        "[READ] Found %s files in %s at source folder: %s",
        (sum(len(files) for files in files_map.values())),
        f"{elapsed_time:.2f}s",
        source_path,
    )

    logging.debug("[READ] End of reading source folder content.")

    return files_map


def resolve_duplicates_and_conflicts(
    files_map: dict[str, list[dict]],
) -> dict[str, list[dict]]:
    """
    Resolve duplicate and conflicting file names by assigning unique output names.

    Duplicate = file has same name and same hash (pure duplicates) -> marked to be skip
    Conflict  = file has same name and different hash -> mark to be copied with a different
                unique name (mitigate potential critical data loss as file will be overwritten)

    Special case: Files without an extension are handled using the key "no_extension".

    The function adds 'output_name' field in each file's dictionary to reflect its resolved
    filename. For conflicting files, a numeric suffix is appended to create a unique name.

    Args:
        files_map (dict[str, list[dict]]): A mapping from file extensions to lists of file
        info dicts.

    Returns:
        dict[str, list[dict]]: The same mapping with resolved 'output_name' fields in each
        file info dict.
    """
    logging.debug("[RESOLVE] Start of resolving duplicates and conflicts.")
    logging.debug(
        "[RESOLVE] Resolving duplicates and conflicts of files mapping: %s", files_map
    )

    output_name_tracker: defaultdict = defaultdict(dict)  # ext -> {name: hash}
    used_output_names: defaultdict = defaultdict(set)  # ext -> set of used output names

    for ext, file_list in files_map.items():
        for file_info in file_list:
            name = file_info["name"]
            hash_sum = file_info["hash"]

            if name in output_name_tracker[ext]:
                if output_name_tracker[ext][name] == hash_sum:
                    # Pure duplicate: same name and hash
                    file_info["output_name"] = None  # Mark to skip
                    logging.debug(
                        "[RESOLVE] File '%s' is marked as duplicate.", file_info["path"]
                    )
                else:
                    # Conflict: same name, different hash
                    # Get name without extension
                    base_name = name[: -len(ext)] if ext != "no_extension" else name
                    # Find available new name
                    counter = 1  # New unique name counter
                    new_name = (
                        f"{base_name}({counter}){ext}"
                        if ext != "no_extension"
                        else f"{base_name}({counter})"
                    )
                    while new_name in used_output_names[ext]:  # Find unique name
                        counter += 1
                        new_name = (
                            f"{base_name}({counter}){ext}"
                            if ext != "no_extension"
                            else f"{base_name}({counter})"
                        )
                    file_info["output_name"] = new_name  # Save new unique name
                    logging.debug(
                        (
                            "[RESOLVE] File '%s' has name conflict, that will be "
                            "resolved by assigning a new name '%s' to the file."
                        ),
                        file_info["path"],
                        new_name,
                    )
                    used_output_names[ext].add(new_name)  # Mark name as used

            else:
                # Unique so far
                file_info["output_name"] = name
                output_name_tracker[ext][name] = hash_sum
                used_output_names[ext].add(name)
                logging.debug(
                    "[RESOLVE] File '%s' will remain it's original name '%s'.",
                    file_info["path"],
                    file_info["output_name"],
                )

    logging.info("[RESOLVE] Duplicates and conflicts resolved successfully.")

    return files_map


async def copy_files(
    files_map_dict: dict[str, list[dict]],
    target_dir_path: AsyncPath,
    target_str: str,
    dry_run: bool = False,
) -> None:
    """Copy mapped files into target directory."""
    logging.info(
        "[COPY] Start of copying files into target folder: %s", target_dir_path
    )
    logging.debug("[COPY] Copying files of files mapping: %s", files_map_dict)

    # Start tracking execution time
    start_time = time.monotonic()

    copied_counter = 0
    failed_counter = 0
    semaphore = asyncio.Semaphore(5)  # limit how many coroutines run concurrently

    async def copy_single_file(file_info: dict):
        nonlocal copied_counter, failed_counter

        async with semaphore:
            # await asyncio.sleep(0.5)  # simulate delay
            ext = get_file_extension(file_info["path"])
            safe_ext = ext.lstrip(".").replace(".", "_") or "no_extension"
            output_path = target_dir_path / safe_ext / file_info["output_name"]
            try:
                await copy_file(file_info["path"], output_path)
                copied_counter += 1
                print_copy_update(copied_counter, total_files, start_time)
                logging.debug(
                    "[COPY] File '%s' copied from '%s' to '%s' ('%s' folder) as '%s'.",
                    file_info["name"],
                    file_info["path"],
                    output_path,
                    safe_ext,
                    file_info["output_name"],
                )
            except OSError as exc:
                failed_counter += 1
                logging.debug(
                    "[COPY] ❌ Failed to copy from '%s' to '%s': %s",
                    file_info["path"],
                    output_path,
                    exc,
                )
                logging.warning(
                    "[COPY] ⚠️  Copying of file '%s' skipped due to error: %s",
                    file_info["name"],
                    file_info["path"],
                )

    # Flatten and filter files that are not pure duplicates
    all_files = [
        file_info
        for entries in files_map_dict.values()
        for file_info in entries
        if file_info.get("output_name")  # skip pure duplicates when value is None
    ]
    total_files = len(all_files)

    if dry_run:
        total_folders = len(files_map_dict.values())
        # Skip coping any files, just show dry run message
        logging.debug(
            "[DRY RUN] Would copy %d files to '%s'",
            total_files,
            target_dir_path,
        )
        print_dry_run_msg(total_files, total_folders, target_str)
        return

    tasks = [copy_single_file(file_info) for file_info in all_files]

    logging.info("[COPY] Copying %s files into '%s'...", total_files, target_dir_path)
    await asyncio.gather(*tasks)

    elapsed_time = time.monotonic() - start_time
    print_copy_summary(copied_counter, target_str, elapsed_time, failed_counter)
    logging.info(
        "[COPY] %d files copied successfully into target '%s' in %s.",
        copied_counter,
        target_dir_path,
        f"{elapsed_time:.2f}s",
    )
