"""Typed dictionary models for file entries used in file processing and output.

Defines the FileEntry TypedDict used to represent file metadata during
mapping, conflict resolution, and reporting.
"""

from __future__ import annotations

from typing import TypedDict, Optional

from aiopath import AsyncPath

class FileEntry(TypedDict):
    """Represents a single file entry in the mapping phase.

    Attributes:
        path (str): Full original path to the file.
        name (str): Original file name.
        size (int): File size in bytes.
        modified (float): Modification time (timestamp).
        output_name (Optional[str]): Name of the file after resolving conflicts. None if duplicate.
    """
    path: AsyncPath
    name: str
    size: int
    hash: str
    modified: float
    output_name: Optional[str]
