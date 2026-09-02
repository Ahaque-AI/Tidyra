"""Scanner — turns a directory path into a list of ``FileEntry``.

The scanner is a thin wrapper over the ``FileSystem`` abstraction. Keeping
it as its own module leaves room for future filtering (e.g. exclusion
lists, hidden-file handling) without bloating the service that calls it.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from tidyra.domain.models import FileEntry
from tidyra.infrastructure.filesystem import FileSystem


def scan_directory(fs: FileSystem, root: Path) -> Sequence[FileEntry]:
    """Scan a directory through the given filesystem."""
    return fs.scan(root)
