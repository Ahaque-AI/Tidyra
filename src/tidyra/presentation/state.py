"""UI state — kept separate from domain models.

The presentation layer can hold view-local data here (current screen,
loading flag, last error, selected folder) without leaking those into
domain objects.
"""

from __future__ import annotations

from collections.abc import Callable, Sequence
from dataclasses import dataclass, field
from enum import StrEnum
from pathlib import Path

from tidyra.application.services import OrganizeService
from tidyra.domain.models import FileEntry
from tidyra.domain.plans import OrganizationPlan, OrganizationResult


class Screen(StrEnum):
    HOME = "home"
    PREVIEW = "preview"
    RESULTS = "results"


@dataclass
class UIState:
    """Mutable view-local state.

    Domain objects flow through unchanged. Only screen navigation,
    loading flags, user-facing errors, and view-local toggles live here.
    """

    service: OrganizeService
    root: Path | None = None
    entries: Sequence[FileEntry] = field(default_factory=tuple)
    plan: OrganizationPlan | None = None
    result: OrganizationResult | None = None
    screen: Screen = Screen.HOME
    loading: bool = False
    error: str | None = None
    # ``recurse_subfolders`` defaults to True so the first scan walks the
    # tree by default — matches the user's expectation that Tidyra
    # organises the whole chosen root, not just its direct children.
    recurse_subfolders: bool = True
    remove_empty_directories: bool = False
    on_navigate: Callable[[], None] | None = field(default=None, repr=False)

    def go(self, screen: Screen) -> None:
        self.screen = screen
        self.refresh()

    def refresh(self) -> None:
        if self.on_navigate is not None:
            self.on_navigate()
