"""
Utility to extract project metadata from `pyproject.toml`.

Uses the built-in `tomllib` module (Python 3.11+) to read version, author,
email, description, urls, etc. from the `pyproject.toml` sections.
"""

from __future__ import annotations  # Enables lazy type evaluation (needed for forward references on Python <3.10)

import logging
from typing import TypedDict

try:
    # Note: `tomllib` is only available in Python 3.11+ (as part of Python default modules).
    import tomllib  # type: ignore[import-not-found]
except ModuleNotFoundError:
    # For Python <3.11, `tomli` is used instead (declared in pyproject.toml).
    import tomli as tomllib  # type: ignore[no-redef]


class ProjectMetadata(TypedDict):
    """Project metadata parsed from pyproject.toml."""

    version: str
    author: str
    email: str
    description: str
    homepage: str


def get_project_metadata() -> ProjectMetadata:
    """
    Parse `pyproject.toml` and return relevant project metadata.

    Returns:
        A dictionary containing version, author, email, description, and homepage, with keys:
            - version: Project version (str)
            - author: Author's name (str)
            - email: Author's email (str)
            - description: Project description (str)
            - homepage: Project homepage URL (str)

    Raises:
        RuntimeError: If the file is missing, malformed, or required keys are not found.
    """
    try:
        with open("pyproject.toml", "rb") as fh:
            data = tomllib.load(fh)
            project = data["project"]
            author = project.get("authors", [{}])[0]
            homepage = data.get("project", {}).get("urls", {}).get("Homepage", "")
            return {
                "version": project["version"],
                "author": author.get("name", "Unknown"),
                "email": author.get("email", ""),
                "description": project.get("description", ""),
                "homepage": homepage,
            }
    except (FileNotFoundError, tomllib.TOMLDecodeError, KeyError) as exc:
        logging.error("Cannot read metadata from pyproject.toml: %s", exc)
        raise RuntimeError(f"Cannot read metadata from pyproject.toml: {exc}") from exc
