"""Filesystem abstraction.

The domain and application layers never touch the real filesystem
directly. All access goes through a ``FileSystem`` implementation. The
production implementation is :class:`LocalFileSystem`; tests can inject
an in-memory fake without ever touching a developer machine.
"""

from __future__ import annotations

import os
import shutil
from collections.abc import Sequence
from errno import EEXIST, ENOTEMPTY
from pathlib import Path
from typing import Protocol, runtime_checkable

from loguru import logger

from tidyra.domain.models import FileEntry


@runtime_checkable
class FileSystem(Protocol):
    """The minimum surface the organizer needs from a filesystem."""

    def scan(self, root: Path, *, recurse: bool = False) -> Sequence[FileEntry]:
        """Return ``FileEntry`` records discovered under ``root``.

        When ``recurse`` is False (default), only direct children are
        returned. Subdirectories appear as ``FileEntry`` with
        ``is_directory=True`` and are skipped during planning.

        When ``recurse`` is True, every regular file under ``root`` is
        returned. Subdirectories are not returned as entries — they are
        walked transparently. ``FileEntry.path`` stays absolute so the
        executor can move the right file; the relative path under ``root``
        is what the strategy uses to compute the destination.
        """
        ...

    def move(self, source: Path, destination: Path) -> None:
        """Move a regular file from source to destination.

        Implementations MUST create parent directories as needed. The
        caller is responsible for confirming the move is safe (the plan
        validator handles that).
        """
        ...

    def exists(self, path: Path) -> bool:
        """Return True if ``path`` exists (file, directory, or symlink)."""
        ...

    def create_directory(self, path: Path) -> None:
        """Create ``path`` and any missing parents.

        No-op if ``path`` already exists.
        """
        ...

    def is_within(self, path: Path, root: Path) -> bool:
        """Return True if ``path`` resolves inside ``root``."""
        ...

    def directories(self, root: Path, *, recurse: bool = False) -> Sequence[Path]:
        """Return real directories under ``root``, deepest first."""
        ...

    def remove_empty_directory(self, path: Path) -> bool:
        """Remove ``path`` only when it is still an empty, real directory."""
        ...

    def set_modified_time(self, path: Path, timestamp: float) -> bool:
        """Set a real directory's modified time without following links."""
        ...


class LocalFileSystem:
    """Concrete ``FileSystem`` backed by :mod:`pathlib` and :mod:`shutil`."""

    def scan(self, root: Path, *, recurse: bool = False) -> Sequence[FileEntry]:
        if not root.exists() or not root.is_dir():
            logger.bind(root=str(root), component="filesystem").warning(
                "scan: root missing or not a directory"
            )
            return ()
        entries: list[FileEntry] = []
        if recurse:
            for child in root.rglob("*"):
                try:
                    # Skip directories — they appear in scan output only as
                    # top-level markers (the strategy treats them as "not
                    # a file" and skips).
                    if child.is_dir() and not child.is_symlink():
                        continue
                    entries.append(self._build_entry(child))
                except OSError:
                    logger.bind(
                        root=str(root),
                        child=str(child),
                        component="filesystem",
                    ).exception("scan: failed to stat entry")
        else:
            for child in root.iterdir():
                try:
                    entries.append(self._build_entry(child))
                except OSError:
                    # One bad entry (e.g. a broken symlink) should not abort
                    # the whole scan. Log it and move on.
                    logger.bind(
                        root=str(root),
                        child=str(child),
                        component="filesystem",
                    ).exception("scan: failed to stat entry")
        logger.bind(
            root=str(root),
            entries=len(entries),
            recurse=recurse,
            component="filesystem",
        ).info("scan complete")
        return entries

    def move(self, source: Path, destination: Path) -> None:
        destination.parent.mkdir(parents=True, exist_ok=True)
        logger.bind(
            source=str(source),
            destination=str(destination),
            component="filesystem",
        ).info("move: starting")
        shutil.move(str(source), str(destination))

    def exists(self, path: Path) -> bool:
        return path.exists()

    def create_directory(self, path: Path) -> None:
        path.mkdir(parents=True, exist_ok=True)
        logger.bind(path=str(path), component="filesystem").debug("create_directory")

    def is_within(self, path: Path, root: Path) -> bool:
        try:
            path.resolve().relative_to(root.resolve())
        except ValueError:
            return False
        return True

    def directories(self, root: Path, *, recurse: bool = False) -> Sequence[Path]:
        if not root.exists() or not root.is_dir():
            return ()
        candidates = root.rglob("*") if recurse else root.iterdir()
        directories: list[Path] = []
        for candidate in candidates:
            try:
                if _is_link_or_junction(candidate) or not candidate.is_dir():
                    continue
                directories.append(candidate)
            except OSError:
                logger.bind(path=str(candidate), component="filesystem").exception(
                    "directory scan: failed to inspect entry"
                )
        return tuple(sorted(directories, key=lambda path: len(path.parts), reverse=True))

    def remove_empty_directory(self, path: Path) -> bool:
        """Use the OS's non-recursive removal as the final emptiness check."""
        if _is_link_or_junction(path):
            return False
        try:
            path.rmdir()
        except OSError as exc:
            if exc.errno in {EEXIST, ENOTEMPTY}:
                return False
            raise
        logger.bind(path=str(path), component="filesystem").info("removed empty directory")
        return True

    def set_modified_time(self, path: Path, timestamp: float) -> bool:
        if _is_link_or_junction(path) or not path.is_dir():
            return False
        os.utime(path, (timestamp, timestamp))
        logger.bind(path=str(path), component="filesystem").debug("set directory modified time")
        return True

    @staticmethod
    def _build_entry(child: Path) -> FileEntry:
        # Use lstat so we don't follow symlinks — recording them honestly
        # is part of the safety contract.
        stat = child.lstat()
        return FileEntry(
            path=child,
            name=child.name,
            extension=child.suffix.lower(),
            size=stat.st_size,
            mtime=stat.st_mtime,
            is_symlink=child.is_symlink(),
            is_directory=child.is_dir() and not child.is_symlink(),
        )


def _is_link_or_junction(path: Path) -> bool:
    """Reject both symbolic links and Windows directory junctions."""
    is_junction = getattr(path, "is_junction", None)
    return path.is_symlink() or (is_junction() if is_junction is not None else False)
