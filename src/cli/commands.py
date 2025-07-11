"""
Command handlers for the File Sorter CLI tool.

Define and manage CLI subcommands and their logic.
"""

from .args_parser import CustomArgumentParser


def parse_args():
    """Parse application arguments"""
    parser = CustomArgumentParser(
        app_title="📁 File Sorter",
        subtitle="Sort and organize your files by extension",
        description=(
            "This CLI tool scans a source directory and copies files into "
            "subfolders in the target directory based on file extensions."
        ),
        epilog=[
            "Created by Oleksandr Romashko",
            "https://github.com/oleksandr-romashko",
        ],
    )
    parser.add_argument("source", help="Source folder to scan and sort files from")
    parser.add_argument("target", help="Target folder to sort files into")

    parser.add_argument(
        "--version",
        action="version",
        version="%(prog)s 0.1.0",  # Please check pyproject.toml app version too
        help="Show the version number and exit",
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
