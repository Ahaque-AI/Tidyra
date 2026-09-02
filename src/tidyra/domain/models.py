"""Domain models — the data shapes the organizer reasons about.

The domain layer is intentionally pure: it imports nothing from
infrastructure, application, or presentation.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True, slots=True)
class FileEntry:
    """A single file discovered during a scan.

    Records what the organizer needs to make a decision. Does not own the
    underlying file and never performs I/O.
    """

    path: Path
    name: str
    extension: str
    size: int
    is_symlink: bool
    is_directory: bool

    @property
    def is_regular_file(self) -> bool:
        """A non-directory, non-symlink file — the only kind we ever move."""
        return not self.is_directory and not self.is_symlink
