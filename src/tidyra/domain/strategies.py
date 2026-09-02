"""Organization strategies — pluggable planners that produce an ``OrganizationPlan``.

The interface is what matters here. This release ships only
:class:`RuleBasedStrategy`; a future ``LLMStrategy`` will satisfy the same
protocol and produce the same plan shape, so the executor never needs to
know which strategy was used.

Strategies MUST NOT touch the filesystem directly. They produce plans;
the executor applies them.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path
from typing import Protocol

from tidyra.domain.models import FileEntry
from tidyra.domain.plans import FileOperation, OrganizationPlan, PlanValidator, SkipReason
from tidyra.domain.rules import OrganizationRule


class OrganizationStrategy(Protocol):
    """A pluggable planner.

    Given a directory root, the entries discovered in it, and a set of
    rules, returns a fully validated :class:`OrganizationPlan`. Strategies
    must be deterministic — two runs over the same inputs must produce
    plans with identical operations.
    """

    def create_plan(
        self,
        root: Path,
        entries: Sequence[FileEntry],
        rules: Sequence[OrganizationRule],
    ) -> OrganizationPlan: ...


class RuleBasedStrategy:
    """Classify each file using rule priority ordering."""

    def __init__(self, validator: PlanValidator) -> None:
        self._validator = validator

    def create_plan(
        self,
        root: Path,
        entries: Sequence[FileEntry],
        rules: Sequence[OrganizationRule],
    ) -> OrganizationPlan:
        candidates = self._propose(root, entries, rules)
        return self._validator.validate(candidates)

    def _propose(
        self,
        root: Path,
        entries: Sequence[FileEntry],
        rules: Sequence[OrganizationRule],
    ) -> tuple[FileOperation, ...]:
        sorted_rules = sorted(rules, key=_priority_key)
        return tuple(self._classify(entry, root, sorted_rules) for entry in entries)

    def _classify(
        self,
        entry: FileEntry,
        root: Path,
        rules: Sequence[OrganizationRule],
    ) -> FileOperation:
        if entry.is_symlink:
            return FileOperation(
                source=entry.path,
                destination=entry.path,
                skip_reason=SkipReason.SYMLINK,
            )
        if entry.is_directory:
            return FileOperation(
                source=entry.path,
                destination=entry.path,
                skip_reason=SkipReason.NOT_A_FILE,
            )

        matches = [rule for rule in rules if rule.matches(entry.extension, entry.name)]
        if not matches:
            return FileOperation(
                source=entry.path,
                destination=entry.path,
                skip_reason=SkipReason.UNMATCHED,
            )

        top = matches[0]
        tied = [rule for rule in matches if rule.priority == top.priority]
        if len(tied) > 1:
            return FileOperation(
                source=entry.path,
                destination=entry.path,
                rule_name=top.name,
                skip_reason=SkipReason.RULE_CONFLICT,
            )

        destination = root / top.destination / entry.name
        return FileOperation(
            source=entry.path,
            destination=destination,
            rule_name=top.name,
        )


def _priority_key(rule: OrganizationRule) -> tuple[int, int]:
    """Sort key: highest priority first, then stable by original order.

    Python's sort is stable, so rules with the same priority keep their
    declared order.
    """
    return (-rule.priority, 0)
