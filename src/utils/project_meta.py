"""
Utility to extract project metadata from `pyproject.toml`.

Uses the built-in `tomllib` module (Python 3.11+) to read version, author,
email, description, urls, etc. from the `pyproject.toml` sections.
"""

import tomllib  # Python 3.11+ only; use `tomli` on earlier versions


def get_project_metadata() -> dict:
    """
    Parse `pyproject.toml` and return relevant project metadata.

    Returns:
        A dictionary containing version, author, email, description, and homepage.

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
        raise RuntimeError(
            f"❌ Cannot read metadata from pyproject.toml: {exc}"
        ) from exc
