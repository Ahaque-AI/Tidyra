"""Organize executor — applies an ``OrganizationPlan`` to a filesystem.

The executor is intentionally separate from the planner so a dry-run mode
(``plan_for`` without ``execute``) and the real run can never diverge:
both consume the same validated plan.
"""

from __future__ import annotations

from tidyra.domain.plans import FileOperation, OrganizationPlan, OrganizationResult
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
        failures: list[tuple[FileOperation, Exception]] = []
        for op in plan.to_execute():
            try:
                self._fs.create_directory(op.destination.parent)
                self._fs.move(op.source, op.destination)
            except Exception as exc:
                failures.append((op, exc))
        return OrganizationResult(plan=plan, failures=tuple(failures))
