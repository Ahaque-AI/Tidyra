"""Tidyra application controller.

Lives in its own module to avoid the circular import between
``app.py`` (entry point) and the views that need to call into it.
"""

from __future__ import annotations

from pathlib import Path

import flet as ft

from tidyra.application.services import OrganizeService
from tidyra.domain.plans import OrganizationPlan
from tidyra.presentation.state import Screen, UIState
from tidyra.presentation.views.home import home_view
from tidyra.presentation.views.preview import preview_view
from tidyra.presentation.views.results import results_view


class TidyraApp:
    """Application controller — mediates between Flet events and the service.

    The presentation layer calls into this controller. The controller
    talks to the application service and mutates the UI state. There is
    no business logic in event handlers.
    """

    def __init__(self, page: ft.Page, state: UIState) -> None:
        self.page = page
        self.state = state
        self.picker: ft.FilePicker | None = None

    # ----- rendering -------------------------------------------------------

    def render(self) -> None:
        self.page.controls.clear()
        match self.state.screen:
            case Screen.HOME:
                self.page.add(home_view(self))
            case Screen.PREVIEW:
                self.page.add(preview_view(self))
            case Screen.RESULTS:
                self.page.add(results_view(self))
        self.page.update()

    # ----- event handlers --------------------------------------------------

    async def pick_folder(self) -> None:
        if self.picker is None:
            return
        result = await self.picker.get_directory_path(
            dialog_title="Choose a folder to organize",
        )
        if result:
            self.state.root = Path(result)
            self.state.error = None
            self.render()

    def scan(self) -> None:
        if self.state.root is None:
            return
        self.state.loading = True
        self.state.error = None
        self.render()
        try:
            plan, entries = self.state.service.plan_for(self.state.root)
            self.state.plan = plan
            self.state.entries = entries
            self.state.screen = Screen.PREVIEW
        except Exception as exc:  # surface user-facing errors at the boundary
            self.state.error = f"Could not scan folder: {exc}"
            self.state.screen = Screen.HOME
        finally:
            self.state.loading = False
        self.render()

    def organize(self) -> None:
        if self.state.plan is None:
            return
        self.state.loading = True
        self.state.error = None
        self.render()
        try:
            result = self.state.service.execute(self.state.plan)
            self.state.result = result
            self.state.screen = Screen.RESULTS
        except Exception as exc:  # surface user-facing errors at the boundary
            self.state.error = f"Could not organize: {exc}"
        finally:
            self.state.loading = False
        self.render()

    def back_home(self) -> None:
        self.state.screen = Screen.HOME
        self.state.plan = None
        self.state.result = None
        self.state.error = None
        self.render()

    # ----- accessors for views ---------------------------------------------

    @property
    def has_executable_plan(self) -> bool:
        plan: OrganizationPlan | None = self.state.plan
        return plan is not None and not plan.is_empty()

    @property
    def service(self) -> OrganizeService:
        return self.state.service
