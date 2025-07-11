"""
Storage module for handling user messages.

This module provides functionality for reading from and writing to a JSON
file that stores messages along with their timestamps. It includes error
handling for file access and JSON serialization issues.
"""

from datetime import datetime, timezone
import json
import os
import logging
from pathlib import Path

from utils.constants import TIMESTAMP_STORAGE_FORMAT


class StorageError(Exception):
    """Custom exception for storage-related errors."""

    def __init__(self, message: str = ""):
        super().__init__(message)


class MessageStorage:
    """
    Manages persistent storage of messages in a JSON file.

    Attributes:
        file_path (Path): The path to the storage file.
    """

    def __init__(self, file_path: Path) -> None:
        # Check for file and its access - fail early
        logging.info("Initializing MessageStorage")
        if not file_path.exists():
            err_msg = "Failed to initialize storage file"
            logging.error(
                "%s. File: %s. %s.",
                err_msg,
                file_path,
                "File either does not exist or has different name or path",
            )
            raise StorageError(err_msg)
        if not os.access(file_path, os.R_OK | os.W_OK):
            raise StorageError("Storage file is not readable or writable.")

        self.__file_path: Path = file_path

    def get_all(self) -> dict:
        """Get all message entries from the storage"""
        # TODO: Future improvement: Limit message count (e.g., only keep the last 100)
        # TODO: or rotate old entries as file will grow very large over time
        try:
            with open(self.__file_path, "r", encoding="utf-8") as fh:
                # Prevent JSONDecodeError if file is empty
                content = fh.read().strip()
                return json.loads(content) if content else {}
        except (
            FileNotFoundError,
            PermissionError,
            IsADirectoryError,
            OSError,
        ) as exc:
            # Issues with storage file or its access
            err_msg = "Error while reading storage file"
            logging.error(
                "%s. File: %s. %s.",
                err_msg,
                self.__file_path,
                "Issue with storage file",
            )
            raise StorageError(err_msg) from exc
        except json.JSONDecodeError as exc:
            # Issues with JSON format during deserialization
            err_msg = "Error while reading storage file."
            logging.error(
                "%s. File: %s. %s.",
                err_msg,
                self.__file_path,
                "Invalid format or corrupted JSON file",
            )
            raise StorageError(err_msg) from exc

    def save_message(self, message_data: dict) -> None:
        """Save message to storage"""
        # Step 1: Mark receive time first
        timestamp = datetime.now(timezone.utc).strftime(TIMESTAMP_STORAGE_FORMAT)

        # Step 2: Read messages from the storage
        storage_data = self.get_all()

        # Step 3: Modify data by adding new message entry
        storage_data[timestamp] = {
            "username": message_data.get("username", ""),
            "message": message_data.get("message", ""),
        }

        try:
            # Step 4: Overwrite entire storage file content
            #         Note: Keep metadata by overwriting file content, not file itself
            with open(self.__file_path, "r+", encoding="utf-8") as fh:
                # Move file pointer at the beginning before writing (overwrite, not append)
                fh.seek(0)
                # Write JSON into storage file
                json.dump(storage_data, fh, indent=2)
                # Remove potential leftover bytes from the previous write
                fh.truncate()
        except (
            FileNotFoundError,
            PermissionError,
            IsADirectoryError,
            OSError,
        ) as exc:
            # Issues with storage file or its access
            err_msg = "Failed to save data to storage file"
            logging.error(
                "%s. File: %s. %s.",
                err_msg,
                self.__file_path,
                "Issue with storage file",
            )
            raise StorageError(err_msg) from exc
        except TypeError as exc:
            # Issues with JSON serialization
            # (e.g., unserializable types like datetime, sets, or custom classes)
            err_msg = "Failed to save data to storage file"
            logging.error(
                "%s. File: %s. %s.",
                err_msg,
                self.__file_path,
                "Storage JSON data contains non-serializable objects",
            )
            raise StorageError(err_msg) from exc
