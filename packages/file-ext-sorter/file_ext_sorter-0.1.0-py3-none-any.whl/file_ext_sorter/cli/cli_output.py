"""
Handles formatted CLI output for file processing tasks.

Includes functions for printing progress updates, summaries, and user feedback
such as spinners, status messages, and error notices. Designed for an enhanced
terminal user experience with color and emoji indicators.
"""

from __future__ import annotations  # Enables lazy type evaluation (Python <3.10)

import time
from typing import List, Optional, Dict

from colorama import Fore, Style

from file_ext_sorter.core.file_entry import FileEntry
from file_ext_sorter.utils.logger_config import get_console_logger

console_logger = get_console_logger()


def get_spinner_dots(start_time: float, spinner: Optional[List[str]] = None) -> str:
    """Return the current spinner frame based on elapsed time.

    Args:
        start_time (float): The monotonic start time to calculate elapsed duration.
        spinner (List[str], optional): A list of frames to use for the spinner.

    Returns:
        str: The current frame in the spinner animation, padded for alignment.
    """
    default_spinner = [".", "..", "...", "...."]
    frames_per_sec = 2  # 2 times per second, e.g. update frame each 0.5 seconds
    spinner = spinner or default_spinner

    elapsed = time.monotonic() - start_time

    current_frame = spinner[int(elapsed * frames_per_sec) % len(spinner)]

    return f"{current_frame:<{max(len(frame) for frame in spinner)}}"


def print_line(
    message: str = "", end: str = "\n", overwrite_prev_line: bool = False
) -> None:
    """Print a line to the console, optionally overwriting the previous one.

    Args:
        message (str): The message to print.
        end (str): The end character (defaults to newline).
        overwrite_prev (bool): If True, overwrites the current line in the terminal.
    """
    prefix = "\r" if overwrite_prev_line else ""
    print(f"{prefix}{message}", end=end, flush=True)


def print_dynamic_mapping_update(found_counter: int, start_time: float) -> None:
    """
    Print a dynamic update showing how many files were found so far.

    Overwrites the previous line to provide a live-updating effect.

    Args:
        found_counter (int): Number of files found.
        start_time (float): Start time for spinner animation.
    """
    spinner_frame = get_spinner_dots(start_time)
    print_line(
        f"🔎 Found {Style.BRIGHT}{found_counter} files{Style.RESET_ALL} so far{spinner_frame}",
        overwrite_prev_line=True,
        end="",
    )


def show_mapping_summary(
    files_map: Dict[str, List[FileEntry]],
    time_to_execute: float,
    skipped_count: int = 0,
) -> None:
    """Print a summary of the file mapping and analysis process.

    Includes grouped counts per extension, along with statistics for duplicates,
    conflicts, and total size.

    Args:
        files_map (dict): Mapping of file extensions to lists of file info dictionaries.
        time_to_execute (float): Total execution time in seconds.
        skipped_count (int, optional): Number of files skipped due to errors.
    """
    total_files: int = 0
    total_duplicates: int = 0
    total_conflicts: int = 0
    total_bytes_to_copy: int = 0

    print_line("", end="", overwrite_prev_line=True)  # overwrite latest dynamic output

    console_logger.info("📁 Files grouped by extension:")
    for extension, entries in sorted(files_map.items()):
        ext_total = len(entries)
        ext_duplicates = 0
        ext_conflicts = 0

        # Keep newest files first (latest modified file as the one to keep if duplicate)
        sorted_entries_by_newest = sorted(
            entries, key=lambda f: f["modified"], reverse=True
        )
        for file_entry in sorted_entries_by_newest:
            output_name = file_entry.get("output_name")
            if output_name is None:  # Duplicate
                ext_duplicates += 1
            elif output_name != file_entry["name"]:  # Conflict
                ext_conflicts += 1
                total_bytes_to_copy += file_entry["size"]
            else:
                total_bytes_to_copy += file_entry["size"]

        duplicates_str = (
            f"{Fore.YELLOW}{ext_duplicates} duplicates{Style.RESET_ALL}"
            if ext_duplicates
            else ""
        )
        conflicts_str = (
            (
                f"{Fore.GREEN}{ext_conflicts} conflict{('s' if ext_conflicts != 1 else '')} "
                f"resolved{Style.RESET_ALL}"
            )
            if ext_conflicts
            else ""
        )

        per_ext_summary = ", ".join(filter(None, [duplicates_str, conflicts_str]))
        per_ext_summary_str = f" ({per_ext_summary})" if per_ext_summary else ""
        log_msg = f"{extension.ljust(12)} {ext_total} files{per_ext_summary_str}"
        console_logger.info("  %s", log_msg)

        total_files += ext_total
        total_duplicates += ext_duplicates
        total_conflicts += ext_conflicts

    # Extra empty line to separate summary
    print_line("")

    # Skipped files
    if skipped_count:
        console_logger.warning(
            "Skipped %d file%s due to unreadable format or permission issues",
            skipped_count,
            "s" if skipped_count != 1 else "",
        )

    # Final summary
    extras = []
    if total_duplicates:
        extras.append(
            (
                f"{Fore.YELLOW}{total_duplicates} duplicate{'s' if total_duplicates != 1 else ''} "
                f"to skip{Style.RESET_ALL}"
            )
        )
    if total_conflicts:
        extras.append(
            (
                f"{Fore.GREEN}{total_conflicts} conflict{'s' if total_conflicts != 1 else ''} "
                f"resolved{Style.RESET_ALL}"
            )
        )

    total_files_f_str = f"{Style.BRIGHT}{total_files} files{Style.RESET_ALL}"
    time_to_execute_f_str = f"{time_to_execute:.2f}s"
    extras_f_str = f" ({', '.join(extras)})" if extras else ""
    console_logger.info(
        "✅ Found %s in %s%s",
        total_files_f_str,
        time_to_execute_f_str,
        extras_f_str,
    )

    # Size to copy
    if total_bytes_to_copy > 0:
        total_mb = total_bytes_to_copy / (1024 * 1024)
        total_mb_formatted_str = f"{total_mb:.2f}"
        console_logger.info("📦 Estimated total to copy: %s MB", total_mb_formatted_str)

    # Extra empty line before further dynamic update
    print_line("")


def print_dynamic_copy_update(
    copied_counter: int, total_files: int, start_time: float
) -> None:
    """Print a dynamic update showing the number of files copied so far.

    Args:
        copied_counter (int): Number of files successfully copied.
        total_files (int): Total number of files to copy.
        start_time (float): The start time for calculating spinner frame.
    """
    spinner_frame = get_spinner_dots(start_time)
    print_line(
        (
            f"📄 Copied {Style.BRIGHT}{copied_counter}{Style.RESET_ALL}/{Style.BRIGHT}{total_files} "
            f"files{Style.RESET_ALL}{spinner_frame}"
        ),
        overwrite_prev_line=True,
        end="",
    )


def show_copy_summary(
    files_number: int, output_path: str, time_to_execute: float, error_count: int = 0
) -> None:
    """Print a final summary after the file copy operation completes.

    Args:
        files_number (int): Total number of files copied.
        output_path (str): Destination directory path.
        time_to_execute (float): Duration of the copy operation.
        error_count (int, optional): Number of copy failures.
    """
    print_line("", end="", overwrite_prev_line=True)  # overwrite latest dynamic output
    total_files_f_str = f"{Style.BRIGHT}{files_number} files{Style.RESET_ALL}"
    output_path_f_str = f"{Style.BRIGHT}{output_path}{Style.RESET_ALL}"
    time_to_execute_str = f"{time_to_execute:.2f}s"
    warning_str = f"\n⚠️  Failed to copy {error_count} files" if error_count else ""
    console_logger.info(
        "✅ Copied %s into '%s' folder in %s%s",
        total_files_f_str,
        output_path_f_str,
        time_to_execute_str,
        warning_str,
    )


def show_dry_run_msg(
    total_files: int, total_folders: int, output_path_str: str
) -> None:
    """Print a message indicating that the dry run was successful."""
    print_line("", end="", overwrite_prev_line=True)  # overwrite latest dynamic output
    console_logger.info("✅ Dry run complete. Copying skipped. No files were copied.")
    total_files_f_str = f"{Style.BRIGHT}{total_files} files{Style.RESET_ALL}"
    total_folders_f_str = f"{Style.BRIGHT}{total_folders} folders{Style.RESET_ALL}"
    output_path_f_str = f"{Style.BRIGHT}{output_path_str}{Style.RESET_ALL}"
    console_logger.info(
        "☝️  Would copy %s into %s at '%s'.",
        total_files_f_str,
        total_folders_f_str,
        output_path_f_str,
    )


def show_interrupt_msg() -> None:
    """Print a message indicating that execution was interrupted."""
    print_line()
    console_logger.warning(
        "Execution interrupted. Sorting was cancelled before completion."
    )
