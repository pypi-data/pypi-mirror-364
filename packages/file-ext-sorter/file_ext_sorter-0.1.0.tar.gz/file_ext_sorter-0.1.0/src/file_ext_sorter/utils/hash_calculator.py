"""Utility for calculating hash of files."""

from __future__ import annotations  # Enables lazy type evaluation (Python <3.10)

import hashlib
from typing import cast

from file_ext_sorter.core.myaiopath import (
    AsyncPath,
)  # aiopath.AsyncPath replacement (support Python 3.8+)


async def get_file_hash(file_path: AsyncPath, chunk_size: int = 65536) -> str:
    """
    Calculate the SHA-256 hash of a file asynchronously.

    Args:
        file_path: The path to the file to be hashed.
        chunk_size: The number of bytes to read at once. Default is 64 KiB.

    Returns:
        The SHA-256 hash of the file as a hexadecimal string.
    """
    hash_sha256 = hashlib.sha256()

    async with file_path.open("rb") as f:
        while chunk := cast(bytes, await f.read(chunk_size)):
            hash_sha256.update(chunk)

    return hash_sha256.hexdigest()
