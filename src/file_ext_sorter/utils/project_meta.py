"""
Utility to extract project metadata using importlib.metadata.

This version avoids runtime dependency on pyproject.toml by using
the installed distribution metadata.
"""

from importlib.metadata import metadata, PackageNotFoundError
from typing import TypedDict


class ProjectMetadata(TypedDict):
    version: str
    author: str
    email: str
    description: str
    homepage: str


def get_project_metadata(distribution_name: str = "file-ext-sorter") -> ProjectMetadata:
    """
    Return relevant metadata for the installed distribution.

    Args:
        distribution_name (str): The package name as declared in pyproject.toml.

    Returns:
        ProjectMetadata: A dict containing version, author, email, description, homepage.

    Raises:
        RuntimeError: If the metadata cannot be found (e.g., not installed).
    """
    try:
        dist_meta = metadata(distribution_name)
        return {
            "version": dist_meta.get("Version", "unknown"),
            "author": dist_meta.get("Author", "unknown"),
            "email": dist_meta.get("Author-email", ""),
            "description": dist_meta.get("Summary", ""),
            "homepage": dist_meta.get("Home-page", ""),
        }
    except PackageNotFoundError as exc:
        raise RuntimeError(
            f"Cannot read installed metadata for package '{distribution_name}'."
        ) from exc
