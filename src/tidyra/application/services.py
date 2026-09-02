"""Application services — the public surface the presentation layer uses.

``OrganizeService`` is the only application-layer object the UI should
talk to. It wires the filesystem, the configuration, and the executor
into a single facade.
"""

from __future__ import annotations

from collections.abc import Sequence
from pathlib import Path

from loguru import logger

from tidyra.application.organize import OrganizeExecutor
from tidyra.application.scanner import scan_directory
from tidyra.domain.models import FileEntry
from tidyra.domain.plans import OrganizationPlan, OrganizationResult, PlanValidator
from tidyra.domain.rules import OrganizationRule
from tidyra.domain.strategies import RuleBasedStrategy
from tidyra.infrastructure.configuration import ConfigService, get_config_service
from tidyra.infrastructure.filesystem import FileSystem


class OrganizeService:
    """Top-level orchestrator: scan → plan → execute."""

    def __init__(
        self,
        fs: FileSystem,
        *,
        config: ConfigService | None = None,
    ) -> None:
        self._fs = fs
        self._config = config or get_config_service()

    @property
    def filesystem(self) -> FileSystem:
        return self._fs

    def rules(self) -> Sequence[OrganizationRule]:
        """Return the active rule list."""
        return self._config.load()

    def rules_source_path(self) -> Path:
        """Path of the TOML file the active rules were loaded from."""
        _, source = self._config.load_with_source()
        return source.path

    def rules_source_origin(self) -> str:
        """``"user"``, ``"cwd"``, or ``"builtin"``."""
        _, source = self._config.load_with_source()
        return source.origin

    def default_user_config_path(self) -> Path:
        """Where the user can drop their own ``rules.toml``."""
        return self._config.default_config_path()

    def plan_for(self, root: Path) -> tuple[OrganizationPlan, Sequence[FileEntry]]:
        """Scan ``root`` and produce a validated plan.

        Returns both the plan and the entries so the UI can show the
        scanner's view without re-scanning.
        """
        entries = scan_directory(self._fs, root)
        validator = PlanValidator(root=root, destination_exists=self._fs.exists)
        strategy = RuleBasedStrategy(validator=validator)
        plan = strategy.create_plan(root=root, entries=entries, rules=self.rules())
        moves = plan.to_execute()
        skips = plan.skipped()
        logger.bind(
            root=str(root),
            entries=len(entries),
            to_move=len(moves),
            skipped=len(skips),
            component="service",
        ).info("plan ready")
        return plan, entries

    def execute(self, plan: OrganizationPlan) -> OrganizationResult:
        """Execute a plan against the configured filesystem."""
        return OrganizeExecutor(self._fs).execute(plan)
