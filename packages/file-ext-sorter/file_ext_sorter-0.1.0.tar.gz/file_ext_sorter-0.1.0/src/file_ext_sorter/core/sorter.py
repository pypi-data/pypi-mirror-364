"""
Core logic for file sorting and copying.

This module provides functionality to:
- Recursively scan a directory and group files by extension.
- Generate SHA-256 hashes for uniqueness checks.
- Resolve filename duplicates and conflicts.
- Copy files to a output directory while preserving uniqueness.
- Provide real-time CLI and logging feedback.
"""

from __future__ import annotations  # Enables lazy type evaluation (Python <3.10)

import asyncio
from collections import defaultdict
import logging
import time
from typing import List, Dict

from file_ext_sorter.core.files import (
    get_file_extension,
    copy_file,
)
from file_ext_sorter.core.file_entry import FileEntry
from file_ext_sorter.cli.cli_output import (
    print_dynamic_mapping_update,
    show_mapping_summary,
    print_dynamic_copy_update,
    show_dry_run_msg,
    show_copy_summary,
)
from file_ext_sorter.utils.hash_calculator import get_file_hash

from .myaiopath import AsyncPath  # replacement aiopath.AsyncPath (support Python 3.8+)


async def read_folder(
    source_path: AsyncPath,
) -> Dict[str, List[FileEntry]]:
    """
    Recursively walk through the source directory and group all files by their extension.

    Returns a mapping of extensions to lists of FileEntry file objects.
    """
    logging.info("[READ] Start reading source folder content at: %s", source_path)

    # Start tracking execution time
    start_time = time.monotonic()

    files_map: Dict[str, List[FileEntry]] = defaultdict(list)
    found_counter = 0
    skipped_counter = 0

    async def walk_dir(path: AsyncPath):
        nonlocal found_counter, skipped_counter

        async for entry in path.iterdir():
            try:
                if await entry.is_file():
                    # await asyncio.sleep(0.05)  # simulate delay
                    ext = get_file_extension(entry) or "no_extension"
                    stat = await entry.stat()
                    size = stat.st_size
                    hash_sum = await get_file_hash(entry)
                    modified = stat.st_mtime  # UNIX timestamp
                    file_entry: FileEntry = {
                        "path": entry,
                        "name": entry.name,
                        "size": size,
                        "hash": hash_sum,
                        "modified": modified,
                        "output_name": None,
                    }
                    files_map[ext].append(file_entry)
                    found_counter += 1
                    print_dynamic_mapping_update(found_counter, start_time)
                elif await entry.is_dir():
                    await walk_dir(entry)
            except OSError as exc:
                skipped_counter += 1
                logging.warning(
                    "[READ] ❌ Error occurred while reading '%s': %s. Skipped unreadable entry.",
                    entry,
                    exc,
                )

    # Perform source directory file mapping, incl. all subdirectories
    logging.info("[READ] Analyzing and mapping files in folder: %s", source_path)
    await walk_dir(source_path)

    # Resolve duplicate and conflicting file names
    files_map = resolve_duplicates_and_conflicts(files_map)

    # Calculate total operation time
    elapsed_time = time.monotonic() - start_time

    # Show summary
    show_mapping_summary(files_map, elapsed_time, skipped_counter)
    logging.info(
        "[READ] Found %s files in %s at source folder: %s",
        (sum(len(files) for files in files_map.values())),
        f"{elapsed_time:.2f}s",
        source_path,
    )

    logging.debug("[READ] End of reading source folder content.")

    return files_map


def resolve_duplicates_and_conflicts(
    files_map: Dict[str, List[FileEntry]],
) -> Dict[str, List[FileEntry]]:
    """
    Resolve duplicate and conflicting file names by assigning unique output names.

    Duplicate = file has same name and same hash (pure duplicates) -> marked to be skip
    Conflict  = file has same name and different hash -> mark to be copied with a different
                unique name (mitigate potential critical data loss as file will be overwritten)

    Special case: Files without an extension are handled using the key "no_extension".

    The function adds 'output_name' field in each file's dictionary to reflect its resolved
    filename. For conflicting files, a numeric suffix is appended to create a unique name.

    Args:
        files_map (Dict[str, List[Entry]]): A mapping from file extensions to lists of file
        info dicts.

    Returns:
        Dict[str, List[Entry]]: The same mapping with resolved 'output_name' fields in each
        file info dict.
    """
    logging.debug("[RESOLVE] Start of resolving duplicates and conflicts.")
    logging.debug(
        "[RESOLVE] Resolving duplicates and conflicts of files mapping: %s", files_map
    )

    skipped_duplicates = 0

    output_name_tracker: defaultdict = defaultdict(dict)  # ext -> {name: hash}
    used_output_names: defaultdict = defaultdict(set)  # ext -> set of used output names

    for ext, file_list in files_map.items():
        for file_entry in file_list:
            name = file_entry["name"]
            hash_sum = file_entry["hash"]

            if name in output_name_tracker[ext]:
                if output_name_tracker[ext][name] == hash_sum:
                    # Pure duplicate: same name and hash
                    file_entry["output_name"] = None  # Mark to skip
                    skipped_duplicates += 1
                    logging.debug(
                        "[RESOLVE] File '%s' is marked as duplicate.",
                        file_entry["path"],
                    )
                else:
                    # Conflict: same name, different hash
                    # Get name without extension
                    base_name = name[: -len(ext)] if ext != "no_extension" else name
                    # Find available new name
                    counter = 1  # New unique name counter
                    new_name = (
                        f"{base_name}({counter}){ext}"
                        if ext != "no_extension"
                        else f"{base_name}({counter})"
                    )
                    while new_name in used_output_names[ext]:  # Find unique name
                        counter += 1
                        new_name = (
                            f"{base_name}({counter}){ext}"
                            if ext != "no_extension"
                            else f"{base_name}({counter})"
                        )
                    file_entry["output_name"] = new_name  # Save new unique name
                    logging.debug(
                        (
                            "[RESOLVE] File '%s' has name conflict, that will be "
                            "resolved by assigning a new name '%s' to the file."
                        ),
                        file_entry["path"],
                        new_name,
                    )
                    used_output_names[ext].add(new_name)  # Mark name as used

            else:
                # Unique so far
                file_entry["output_name"] = name
                output_name_tracker[ext][name] = hash_sum
                used_output_names[ext].add(name)
                logging.debug(
                    "[RESOLVE] File '%s' will retain its original name '%s'.",
                    file_entry["path"],
                    file_entry["output_name"],
                )

    logging.info("[RESOLVE] Skipped %d pure duplicate files.", skipped_duplicates)
    logging.info("[RESOLVE] Duplicates and conflicts resolved successfully.")

    return files_map


async def copy_files(
    files_map_dict: Dict[str, List[FileEntry]],
    output_dir_path: AsyncPath,
    output_str: str,
    dry_run: bool = False,
) -> None:
    """Copy mapped files into output directory."""
    logging.info(
        "[COPY] Start of copying files into output folder: %s", output_dir_path
    )
    logging.debug("[COPY] Copying files of files mapping: %s", files_map_dict)

    # Start tracking execution time
    start_time = time.monotonic()

    copied_counter = 0
    failed_counter = 0
    semaphore = asyncio.Semaphore(5)  # limit how many coroutines run concurrently

    async def copy_single_file(file_entry: FileEntry):
        nonlocal copied_counter, failed_counter

        async with semaphore:
            # await asyncio.sleep(0.5)  # simulate delay
            ext = get_file_extension(file_entry["path"])
            safe_ext = ext.lstrip(".").replace(".", "_") or "no_extension"
            output_name = file_entry["output_name"]
            output_path = ""
            try:
                if output_name is None:
                    raise ValueError("output_name can't be None")
                output_path = output_dir_path / safe_ext / output_name
                await copy_file(file_entry["path"], output_path)
                copied_counter += 1
                print_dynamic_copy_update(copied_counter, total_files, start_time)
                logging.debug(
                    "[COPY] File '%s' copied from '%s' to '%s' ('%s' folder) as '%s'.",
                    file_entry["name"],
                    file_entry["path"],
                    output_path,
                    safe_ext,
                    file_entry["output_name"],
                )
            except (OSError, ValueError) as exc:
                failed_counter += 1
                logging.debug(
                    "[COPY] ❌ Failed to copy from '%s' to '%s': %s",
                    file_entry["path"],
                    output_path,
                    exc,
                )
                logging.warning(
                    "[COPY] ⚠️  Copying of file '%s' skipped due to error: %s",
                    file_entry["name"],
                    file_entry["path"],
                )

    # Flatten and filter files that are not pure duplicates
    all_files = []
    for entries in files_map_dict.values():
        for file_entry in entries:
            if file_entry.get("output_name"):  # skip pure duplicates when value is None
                all_files.append(file_entry)
    total_files = len(all_files)

    if dry_run:
        total_folders = len(files_map_dict.values())
        # Skip coping any files, just show dry run message
        show_dry_run_msg(total_files, total_folders, output_str)
        logging.debug(
            "[DRY RUN] Would copy %d files to '%s'",
            total_files,
            output_dir_path,
        )
        return

    tasks = [copy_single_file(file_entry) for file_entry in all_files]

    logging.info("[COPY] Copying %s files into '%s'...", total_files, output_dir_path)
    await asyncio.gather(*tasks)

    elapsed_time = time.monotonic() - start_time
    show_copy_summary(copied_counter, output_str, elapsed_time, failed_counter)
    logging.info(
        "[COPY] %d files copied successfully into output '%s' in %s.",
        copied_counter,
        output_dir_path,
        f"{elapsed_time:.2f}s",
    )
