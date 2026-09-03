"""Organization plans — the central artifact that flows through the system.

A plan carries both executable and skipped operations so the preview can
show the full picture. The same plan is what the executor runs, which
means the user never sees a plan that differs from what gets executed.
"""

from __future__ import annotations

import dataclasses
from collections.abc import Callable, Sequence
from dataclasses import dataclass
from enum import StrEnum
from pathlib import Path


class SkipReason(StrEnum):
    """Why an operation will not be executed.

    Every skipped operation carries one of these so the preview can explain
    what *would* have happened, and why the executor will leave it alone.
    """

    UNMATCHED = "unmatched"
    SYMLINK = "symlink"
    NOT_A_FILE = "not_a_file"
    OUTSIDE_ROOT = "outside_root"
    RULE_CONFLICT = "rule_conflict"
    DESTINATION_EXISTS = "destination_exists"
    NO_OP = "no_op"
    NESTED_DESTINATION = "nested_destination"


@dataclass(frozen=True, slots=True)
class FileOperation:
    """A single source → destination move operation.

    ``skip_reason`` is ``None`` when the operation will execute. When set,
    the executor will skip it and the preview can show the reason.
    """

    source: Path
    destination: Path
    rule_name: str | None = None
    skip_reason: SkipReason | None = None
    date_folder: Path | None = None
    source_mtime: float | None = None

    @property
    def will_execute(self) -> bool:
        return self.skip_reason is None


@dataclass(frozen=True, slots=True)
class DirectoryRemoval:
    """An explicitly confirmed directory that may be removed only if empty."""

    path: Path


@dataclass(frozen=True, slots=True)
class OrganizationPlan:
    """A complete plan for one root directory.

    Carries the root and every operation (executable and skipped) so the
    preview and the executor consume a single, consistent view.
    """

    root: Path
    operations: tuple[FileOperation, ...] = ()
    directory_removals: tuple[DirectoryRemoval, ...] = ()

    def to_execute(self) -> tuple[FileOperation, ...]:
        return tuple(op for op in self.operations if op.will_execute)

    def skipped(self) -> tuple[FileOperation, ...]:
        return tuple(op for op in self.operations if not op.will_execute)

    def date_folder_updates(self) -> tuple[Path, ...]:
        """Date folders whose modified times can be refreshed from planned files."""
        seen: set[Path] = set()
        for op in self.operations:
            if op.skip_reason not in {None, SkipReason.NO_OP} or op.date_folder is None:
                continue
            seen.add(op.date_folder)
        return tuple(sorted(seen))

    def is_empty(self) -> bool:
        return (
            not any(op.will_execute for op in self.operations)
            and not self.directory_removals
            and not self.date_folder_updates()
        )


@dataclass(frozen=True, slots=True)
class OrganizationResult:
    """What happened when an :class:`OrganizationPlan` was executed."""

    plan: OrganizationPlan
    failures: tuple[tuple[FileOperation, Exception], ...] = ()
    removed_directories: tuple[Path, ...] = ()
    directory_removal_failures: tuple[tuple[Path, Exception], ...] = ()

    @property
    def succeeded(self) -> tuple[FileOperation, ...]:
        return self.plan.to_execute()

    @property
    def moved_count(self) -> int:
        return len(self.succeeded) - len(self.failures)


class PlanValidator:
    """The single source of safety truth.

    Inspects each candidate operation against the safety rules and
    produces an :class:`OrganizationPlan` with ``skip_reason`` filled in
    where appropriate. The validator delegates filesystem-existence
    checks to a caller-provided callable so the domain layer stays
    independent of any concrete filesystem.
    """

    def __init__(
        self,
        root: Path,
        *,
        destination_exists: Callable[[Path], bool] | None = None,
    ) -> None:
        self._root = root.resolve()
        self._destination_exists: Callable[[Path], bool] = (
            destination_exists if destination_exists is not None else _never_exists
        )

    @property
    def root(self) -> Path:
        return self._root

    def validate(
        self,
        operations: Sequence[FileOperation],
        directory_removals: Sequence[DirectoryRemoval] = (),
    ) -> OrganizationPlan:
        """Apply safety checks and return the final plan.

        Operations already carrying a ``skip_reason`` are passed through
        unchanged — the validator does not re-judge them.
        """
        validated = tuple(self._check(op) for op in operations)
        safe_removals = tuple(
            removal
            for removal in directory_removals
            if self._is_removable_directory(removal.path)
        )
        return OrganizationPlan(
            root=self._root,
            operations=validated,
            directory_removals=safe_removals,
        )

    def _check(self, op: FileOperation) -> FileOperation:
        if op.skip_reason is not None:
            return op

        source = (
            op.source.resolve() if op.source.is_absolute() else (self._root / op.source).resolve()
        )
        destination = (
            op.destination.resolve()
            if op.destination.is_absolute()
            else (self._root / op.destination).resolve()
        )

        if not self._is_within(source, self._root):
            return self._with_skip(op, source, destination, SkipReason.OUTSIDE_ROOT)
        if not self._is_within(destination, self._root):
            return self._with_skip(op, source, destination, SkipReason.OUTSIDE_ROOT)
        if source == destination:
            return self._with_skip(op, source, destination, SkipReason.NO_OP)
        if self._destination_exists(destination):
            return self._with_skip(op, source, destination, SkipReason.DESTINATION_EXISTS)

        date_folder = self._safe_date_folder(op.date_folder)
        return dataclasses.replace(
            op,
            source=source,
            destination=destination,
            date_folder=date_folder,
        )

    @staticmethod
    def _is_within(path: Path, root: Path) -> bool:
        try:
            path.relative_to(root)
        except ValueError:
            return False
        return True

    def _is_removable_directory(self, path: Path) -> bool:
        """Allow only non-root directories lexically contained by the plan root."""
        resolved = path.resolve()
        return resolved != self._root and self._is_within(resolved, self._root)

    def _safe_date_folder(self, path: Path | None) -> Path | None:
        if path is None:
            return None
        resolved = path.resolve()
        return resolved if resolved != self._root and self._is_within(resolved, self._root) else None

    @staticmethod
    def _with_skip(
        op: FileOperation,
        source: Path,
        destination: Path,
        reason: SkipReason,
    ) -> FileOperation:
        return dataclasses.replace(
            op,
            source=source,
            destination=destination,
            skip_reason=reason,
        )


def _never_exists(_path: Path) -> bool:
    """Default ``destination_exists`` callable — assume nothing exists."""
    return False
