"""
Command handlers for the CLI.

Defines and manages CLI subcommands and their logic.
"""

from utils.project_meta import get_project_metadata

from .parser import CustomArgumentParser

metadata = get_project_metadata()


def parse_args():
    """Parse application arguments."""

    parser = CustomArgumentParser(
        app_title="📁 File Sorter",
        subtitle="Sort and organize your files by extension",
        description=(
            f"v{metadata['version']}"
            "\n\nThis CLI tool scans a source directory and copies files into "
            "subfolder in the target directory based on file extensions."
            "\n\nNotes to some definitions:"
            "\n  duplicate - file with the same file name and content (skipped from copying)"
            "\n  conflict - file with the same file name "
            "and different content (resolved by new name)"
        ),
        epilog=[
            f"Created by {metadata['author']}",
            f"{metadata['homepage']}",
        ],
    )
    parser.add_argument("source", help="Source folder to scan and sort files from")
    parser.add_argument("target", help="Target folder to sort files into")
    parser.add_argument(
        "--version",
        action="version",
        version=f"v{metadata['version']}",
        help="Show the version number and exit",
    )
    parser.add_argument(
        "--debug", action="store_true", help="Enable debug logging to console"
    )

    # TODO: Add optional args in the future --dry-run
    # *: --dry-run - Possibility to run without actual copying (scan & analyze + logging only)
    # *              Use --dry-run to simulate sorting without copying files.
    # parser.add_argument(
    #     "--dry-run",
    #     action="store_true",
    #     help="Simulate directory analysis and sorting without actual files copying.",
    # )

    # TODO: Add optional args in the future --exclude
    # *: --exclude - Possibility to exclude certain file types
    # parser.add_argument(
    #     "--exclude",
    #     nargs="+",
    #     metavar="EXT",
    #     help="List of file extensions to exclude from sorting (e.g. .txt .jpg)",
    # )

    return parser.parse_args()
