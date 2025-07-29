"""
Custom AsyncPath class to replace aiopath, compatible with Python 3.8+.

Implements the exact features used in your project:
- Async methods using asyncio.to_thread()
- Works as a drop-in replacement for aiopath.AsyncPath
- Only includes methods your project uses

You can gradually uncomment each method and test.
"""

from __future__ import annotations  # Enables lazy type evaluation (Python <3.10)

import asyncio

from collections.abc import AsyncIterator
from concurrent.futures import Executor
import functools
import os
from pathlib import Path
from typing import List, Optional, Callable, Union, Literal, AsyncContextManager, Any

import aiofiles
from aiofiles.threadpool.binary import AsyncBufferedReader
from aiofiles.threadpool.text import AsyncTextIOWrapper

if not hasattr(asyncio, "to_thread"):
    # asyncio.to_thread() was introduced in Python 3.9
    # here we backport asyncio.to_thread() to support it in Python 3.8
    async def to_thread(func: Callable[..., Any], /, *args: Any, **kwargs: Any) -> Any:
        """Run func in a separate thread (backport for Python 3.8)."""
        loop = asyncio.get_event_loop()
        return await loop.run_in_executor(
            None, functools.partial(func, *args, **kwargs)
        )

    asyncio.to_thread = to_thread


class AsyncPath:
    """
    A lightweight async wrapper for pathlib.Path with aiofiles integration.

    Designed as a minimal replacement for aiopath.AsyncPath, with only project-specific methods.
    """

    def __init__(self, path: Union[str, Path]) -> None:
        self._path = Path(path)

    def __truediv__(self, key: str) -> AsyncPath:
        """Support path joining via `/` operator."""
        return AsyncPath(self._path / key)

    def __str__(self) -> str:
        return str(self._path)

    def __repr__(self) -> str:
        """Represent the AsyncPath as a string for debugging."""
        return f"AsyncPath({self._path!r})"

    def __fspath__(self) -> str:
        """
        Allow use of AsyncPath in functions that expect os.PathLike (like open()).
        Example: os.open(os.fspath(my_async_path))
        """
        return str(self._path)

    @property
    def parent(self) -> AsyncPath:
        """Return the parent directory."""
        return AsyncPath(self._path.parent)

    @property
    def suffixes(self) -> List[str]:
        """Return list of file suffixes (e.g. ['.tar', '.gz'])."""
        return self._path.suffixes

    @property
    def name(self) -> str:
        """The final path component (e.g. filename or dirname)."""
        return self._path.name

    async def resolve(self) -> AsyncPath:
        """Return the absolute (resolved) path as AsyncPath."""
        return AsyncPath(await asyncio.to_thread(self._path.resolve))

    async def exists(self) -> bool:
        """Check if the path exists on disk."""
        return await asyncio.to_thread(self._path.exists)

    async def is_file(self) -> bool:
        """Check if the path is a file."""
        return await asyncio.to_thread(self._path.is_file)

    async def is_dir(self) -> bool:
        """Check if the path is a directory."""
        return await asyncio.to_thread(self._path.is_dir)

    async def mkdir(self, parents: bool = False, exist_ok: bool = False) -> None:
        """Create a directory at this path."""
        await asyncio.to_thread(self._path.mkdir, parents=parents, exist_ok=exist_ok)

    async def stat(self) -> os.stat_result:
        """Perform an os.stat() call on the path."""
        return await asyncio.to_thread(self._path.stat)

    async def iterdir(self) -> AsyncIterator[AsyncPath]:
        """Asynchronously iterate over directory contents."""
        entries = await asyncio.to_thread(list, self._path.iterdir())
        for entry in entries:
            yield AsyncPath(entry)

    def open(
        self,
        mode: Literal["r", "rb"] = "rb",
        buffering: int = -1,
        encoding: Optional[str] = None,
        errors: Optional[str] = None,
        newline: Optional[str] = None,
        closefd: bool = True,
        opener: Optional[Callable] = None,
        *,
        loop: Optional[asyncio.AbstractEventLoop] = None,
        executor: Optional[Executor] = None,
    ) -> AsyncContextManager[Union[AsyncBufferedReader, AsyncTextIOWrapper]]:
        """
        Open the file asynchronously using aiofiles.

        Supports both text and binary modes, and works as an async context manager.
        Returns an aiofiles-compatible async stream (reader or text wrapper).

        Args:
            mode: File mode (e.g. "r", "rb"). Defaults to "rb".
            buffering: Buffering policy (-1 to use default buffering).
            encoding: Text encoding (required for text mode).
            errors: How to handle encoding/decoding errors.
            newline: Controls universal newlines mode (text mode only).
            closefd: Whether to close the file descriptor.
            opener: Custom opener; see built-in open() for details.
            loop: Optional event loop (not needed in most cases).
            executor: Optional custom executor for thread execution.

        Returns:
            An async context manager yielding an aiofiles stream.
        """
        return aiofiles.open(
            self,
            mode=mode,  # type: ignore[reportArgumentType]
            buffering=buffering,
            encoding=encoding,
            errors=errors,
            newline=newline,
            closefd=closefd,
            opener=opener,
            loop=loop,
            executor=executor,
        )
