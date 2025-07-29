"""
Command handlers for the CLI.

Defines and manages CLI subcommands and their logic.
"""

from __future__ import annotations  # Enables lazy type evaluation (Python <3.10)

from argparse import Namespace

from file_ext_sorter.utils.project_meta import get_project_metadata

from .parser import CustomArgumentParser

metadata: dict = get_project_metadata()


def parse_args() -> Namespace:
    """Parse application arguments."""

    parser = CustomArgumentParser(
        app_title="🔀 File Sorter",
        subtitle="Sort and organize your files by extension",
        description=(
            f"v{metadata['version']}"
            "\n\nThis CLI tool scans a source directory and copies files into "
            "subfolders in the output directory based on file extensions."
            "\n\nNotes on terminology:"
            "\n  duplicate - file with the same file name and content (skipped from copying)"
            "\n  conflict - file with the same file name "
            "and different content (resolved by new name)"
        ),
        epilog="\n".join(
            [
                f"Created by {metadata['author']}",
                f"{metadata['homepage']}",
            ]
        ),
    )
    parser.add_argument(
        "source", help="folder to scan and sort files from (should exist)"
    )
    parser.add_argument("output", help="folder to sort files into (may not exist)")
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="preview the scan and sort result without copying any files.",
    )
    parser.add_argument(
        "--debug", action="store_true", help="enable debug logging to console"
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"v{metadata['version']}",
        help="show the version number and exit",
    )

    return parser.parse_args()
