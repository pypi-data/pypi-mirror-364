"""Entry point for the async CLI file sorter application."""

from __future__ import annotations  # Enables lazy type evaluation (Python <3.10)

import asyncio
import logging
import sys
from argparse import Namespace


import colorama

from file_ext_sorter.core.myaiopath import (
    AsyncPath,
)  # custom replacement for aiopath.AsyncPath to support Python 3.8+

from file_ext_sorter.cli.cli import parse_args
from file_ext_sorter.cli.cli_output import show_interrupt_msg
from file_ext_sorter.core.files import validate_source_dir, validate_output_dir
from file_ext_sorter.core.sorter import read_folder, copy_files
from file_ext_sorter.utils.exit_codes import ExitCode
from file_ext_sorter.utils.logger_config import configure_logging, get_console_logger

colorama.init(autoreset=True)

console_logger = get_console_logger()


async def sort_files(source_dir: str, output_dir: str, dry_run: bool = False) -> None:
    """
    Sort files from source directory into structured folders in the output location.

    Args:
        source_dir: Path to the directory with unsorted files.
        output_dir: Path where sorted files will be placed.
        dry_run: Flag for dry-run simulation without actual files copying
    """
    logging.info(
        "[SORTING] Start sorting files with app args: source '%s' and output '%s'.",
        source_dir,
        output_dir,
    )

    # Resolve real paths
    source_dir_path = await AsyncPath(source_dir).resolve()
    output_dir_path = await AsyncPath(output_dir).resolve()
    logging.debug(
        "[SORTING] Source path '%s' resolved: %s", source_dir, source_dir_path
    )
    logging.debug(
        "[SORTING] Output path '%s' resolved: %s", output_dir, output_dir_path
    )

    # Validate paths
    if not await validate_source_dir(source_dir_path, source_dir):
        sys.exit(ExitCode.SOURCE_VALIDATION_ERROR)
    if not await validate_output_dir(output_dir_path, output_dir):
        sys.exit(ExitCode.OUTPUT_VALIDATION_ERROR)
    logging.debug(
        "[VALIDATION] Source path '%s' and output path '%s' validated successfully.",
        source_dir_path,
        output_dir_path,
    )

    # Scan and categorize files
    mapped_files_dict = await read_folder(source_dir_path)

    # Copy files to structured folders
    await copy_files(mapped_files_dict, output_dir_path, output_dir, dry_run)


async def run_file_sorter() -> None:
    """Run app: parses CLI args and starts sorting."""
    # Parse CLI arguments
    args: Namespace = parse_args()
    source_dir: str = args.source
    output_dir: str = args.output
    debug: bool = args.debug
    dry_run: bool = args.dry_run

    if debug:
        logging.info("[APP] Debug enabled. Enable debug logging to console.")
    if dry_run:
        logging.info(
            "[APP] Dry run enabled. No files will be copied. Simulating sort operation only."
        )

    configure_logging(debug=debug, level=logging.INFO)

    logging.debug("[APP] APPLICATION STARTED.")

    # Call the main app logic
    await sort_files(source_dir, output_dir, dry_run=dry_run)

    logging.debug("[APP] APPLICATION STOPPED.")


def main():
    """Main entry point"""
    try:
        asyncio.run(run_file_sorter())
    except KeyboardInterrupt:
        show_interrupt_msg()
        logging.info("[APP] User interrupted execution with Ctrl+C. Exiting app...")
        sys.exit(ExitCode.SUCCESS)
    except Exception as e:
        console_logger.error(
            "Unexpected error occurred. Please use --debug flag to see detailed logs. Exiting..."
        )
        logging.error("[APP] Unhandled exception: %s", e, exc_info=True)
        sys.exit(ExitCode.GENERAL_ERROR)


if __name__ == "__main__":
    main()
