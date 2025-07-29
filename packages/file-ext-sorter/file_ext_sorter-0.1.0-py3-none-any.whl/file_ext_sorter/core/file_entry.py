"""
Typed dictionary models for file entries used in file processing and output.

Defines the FileEntry TypedDict used to represent file metadata during
mapping, conflict resolution, and reporting.
"""

from __future__ import annotations  # Enables lazy type evaluation (Python <3.10)

from typing import TypedDict, Optional

from .myaiopath import AsyncPath  # aiopath.AsyncPath replacement (support Python 3.8+)


class FileEntry(TypedDict):
    """
    Represents a single file entry in the mapping phase.

    Attributes:
        path (AsyncPath): Full original path to the file.
        name (str): Original file name.
        size (int): File size in bytes.
        hash (str): SHA-256 hash of file contents.
        modified (float): Modification time (UNIX timestamp).
        output_name (Optional[str]): Resolved name used for file output.
    """

    path: AsyncPath
    name: str
    size: int
    hash: str
    modified: float
    output_name: Optional[str]
