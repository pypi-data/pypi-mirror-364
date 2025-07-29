"""
File handling utilities.

Provides async functions to get file extensions, copy files,
and validate source and output directory paths.
"""

from __future__ import annotations  # Enables lazy type evaluation (Python <3.10)

import logging

import aioshutil

from file_ext_sorter.utils.logger_config import get_console_logger

from .myaiopath import AsyncPath  # aiopath.AsyncPath replacement (support Python 3.8+)


console_logger = get_console_logger()


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
        "[COPY] Copied file '%s' from '%s' as '%s' to '%s'.",
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
        console_logger.error("Source path '%s' not found.", origin_path_str)
        logging.error(
            "[VALIDATION] ❌ Source path '%s' not found at '%s'", origin_path_str, path
        )
        return False
    if not await validate_path_is_dir(path):
        console_logger.error("Source path '%s' should be a folder.", origin_path_str)
        logging.error(
            "[VALIDATION] ❌ Source path '%s' at '%s' is not a directory.",
            origin_path_str,
            path,
        )
        return False
    if await validate_dir_is_empty(path):
        console_logger.warning(
            "Source folder '%s' is empty. No files to sort.", origin_path_str
        )
        logging.warning(
            "[VALIDATION] ⚠️  No files found in source folder '%s' at path '%s'. No files to sort.",
            origin_path_str,
            path,
        )
        return False
    return True


async def validate_output_dir(path: AsyncPath, origin_path_str: str) -> bool:
    """Validate that the output path is either non-existent or a directory."""
    if await validate_path_exists(path):
        if not await validate_path_is_dir(path):
            console_logger.error(
                "Output path '%s' should be a folder.", origin_path_str
            )
            logging.error(
                "[VALIDATION] ❌ Output path '%s' exists at '%s' and should be a folder.",
                origin_path_str,
                path,
            )
            return False
        logging.info(
            "[VALIDATION] Output path '%s' exists at '%s'. Using existing output folder.",
            origin_path_str,
            path,
        )
    else:
        logging.info(
            (
                "[VALIDATION] Output path '%s' not found at '%s' "
                "and new output folder will be created."
            ),
            origin_path_str,
            path,
        )
    return True
