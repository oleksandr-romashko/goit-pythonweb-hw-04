"""
File handling utilities.

Provides async functions to get file extensions, copy files,
and validate source and target directory paths.
"""

import logging

from aiopath import AsyncPath  # type: ignore
import aioshutil


def get_file_extension(file_path: AsyncPath) -> str:
    """Retrieve full compound file extension (e.g. '.tar.gz')."""
    return "".join(file_path.suffixes).lower() if file_path.suffixes else ""


async def copy_file(from_path: AsyncPath, to_path: AsyncPath) -> None:
    """Copy a file to the given full output path."""
    destination_dir = to_path.parent

    # Ensure the destination subdirectory exists
    await destination_dir.mkdir(parents=True, exist_ok=True)

    # Perform the copy
    await aioshutil.copy(from_path, to_path)
    logging.debug(
        "Copied file '%s' from '%s' as '%s' to '%s'.",
        from_path.name,
        from_path,
        to_path.name,
        to_path,
    )


async def validate_path_exists(path: AsyncPath) -> bool:
    """Check if path entry exists."""
    return await path.exists()


async def validate_path_is_dir(path: AsyncPath) -> bool:
    """Checks if path entry is a directory."""
    return await path.is_dir()


async def validate_dir_is_empty(path: AsyncPath) -> bool:
    """Check whether directory is empty."""
    async for _ in path.iterdir():
        return False
    return True


async def validate_source_dir(path: AsyncPath, origin_path_str: str) -> bool:
    """Validate that the source path exists, is a directory, and is not empty."""
    if not await validate_path_exists(path):
        print("❌ Error: Source path not found.")
        logging.error("Source path '%s' not found at '%s'", origin_path_str, path)
        return False
    if not await validate_path_is_dir(path):
        print("❌ Error: Source path should be a folder.")
        logging.error(
            "Source path '%s' at '%s' is not a directory.", origin_path_str, path
        )
        return False
    if await validate_dir_is_empty(path):
        print(f"⚠️ Source folder '{origin_path_str}' is empty. No files to sort.")
        logging.warning(
            "No files found to copy in '%s' at path '%s'.", origin_path_str, path
        )
        return False
    return True


async def validate_target_dir(path: AsyncPath, origin_path_str: str) -> bool:
    """Validate that the target path is either non-existent or a directory."""
    if await validate_path_exists(path):
        if not await validate_path_is_dir(path):
            print("❌ Error: Target path should be a folder.")
            logging.error(
                "Target path '%s' exists at '%s' and should be a folder.",
                origin_path_str,
                path,
            )
            return False
        logging.info(
            "Target path '%s' exists at '%s'. Using existing target folder.",
            origin_path_str,
            path,
        )
    return True
