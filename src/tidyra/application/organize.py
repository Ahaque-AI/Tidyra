"""Organize executor — applies an ``OrganizationPlan`` to a filesystem.

The executor is intentionally separate from the planner so a dry-run mode
(``plan_for`` without ``execute``) and the real run can never diverge:
both consume the same validated plan.
"""

from __future__ import annotations

from pathlib import Path

from loguru import logger

from tidyra.domain.plans import FileOperation, OrganizationPlan, OrganizationResult, SkipReason
from tidyra.infrastructure.filesystem import FileSystem


class OrganizeExecutor:
    """Apply the executable operations of a plan against a filesystem."""

    def __init__(self, fs: FileSystem) -> None:
        self._fs = fs

    def execute(self, plan: OrganizationPlan) -> OrganizationResult:
        """Move each executable file. Failures are captured, not raised.

        Returns an :class:`OrganizationResult` containing the original plan
        and a tuple of ``(operation, exception)`` pairs for any moves that
        failed. One bad file does not abort the run.
        """
        to_execute = plan.to_execute()
        logger.bind(
            root=str(plan.root),
            total=len(to_execute),
            component="executor",
        ).info("execute: starting plan")

        failures: list[tuple[FileOperation, Exception]] = []
        date_folder_times: dict[Path, float] = {}
        for op in plan.operations:
            if (
                op.skip_reason in {None, SkipReason.NO_OP}
                and op.date_folder is not None
                and op.source_mtime is not None
            ):
                prior = date_folder_times.get(op.date_folder)
                date_folder_times[op.date_folder] = (
                    op.source_mtime if prior is None else max(prior, op.source_mtime)
                )
        for op in to_execute:
            log = logger.bind(
                source=str(op.source),
                destination=str(op.destination),
                rule=op.rule_name,
                component="executor",
            )
            try:
                self._fs.create_directory(op.destination.parent)
                self._fs.move(op.source, op.destination)
                log.info("moved")
            except Exception as exc:
                log.bind(error_type=type(exc).__name__).exception("move failed")
                failures.append((op, exc))

        for path, timestamp in date_folder_times.items():
            try:
                self._fs.set_modified_time(path, timestamp)
            except Exception as exc:
                logger.bind(
                    path=str(path), error_type=type(exc).__name__, component="executor"
                ).exception("set date folder modified time failed")

        removed_directories: list[Path] = []
        directory_removal_failures: list[tuple[Path, Exception]] = []
        for removal in plan.directory_removals:
            try:
                if self._fs.remove_empty_directory(removal.path):
                    removed_directories.append(removal.path)
            except Exception as exc:
                logger.bind(
                    path=str(removal.path), error_type=type(exc).__name__, component="executor"
                ).exception("empty directory removal failed")
                directory_removal_failures.append((removal.path, exc))

        logger.bind(
            root=str(plan.root),
            moved=len(to_execute) - len(failures),
            failed=len(failures),
            component="executor",
        ).info("execute: complete")
        return OrganizationResult(
            plan=plan,
            failures=tuple(failures),
            removed_directories=tuple(removed_directories),
            directory_removal_failures=tuple(directory_removal_failures),
        )
