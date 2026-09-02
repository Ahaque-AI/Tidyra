"""Tidyra application controller.

Lives in its own module to avoid the circular import between
``app.py`` (entry point) and the views that need to call into it.
"""

from __future__ import annotations

from pathlib import Path

import flet as ft
from loguru import logger

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
        logger.bind(
            screen=self.state.screen.value,
            loading=self.state.loading,
            has_error=bool(self.state.error),
            component="controller",
        ).debug("render")
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
            logger.bind(component="controller").warning(
                "pick_folder invoked before picker was installed"
            )
            return
        result = await self.picker.get_directory_path(
            dialog_title="Choose a folder to organize",
        )
        if result:
            self.state.root = Path(result)
            self.state.error = None
            logger.bind(
                root=str(self.state.root),
                component="controller",
            ).info("folder selected")
            self.render()
        else:
            logger.bind(component="controller").debug("folder selection cancelled")

    def scan(self) -> None:
        if self.state.root is None:
            return
        self.state.loading = True
        self.state.error = None
        self.render()
        logger.bind(root=str(self.state.root), component="controller").info("scan: started")
        try:
            plan, entries = self.state.service.plan_for(self.state.root)
            self.state.plan = plan
            self.state.entries = entries
            self.state.screen = Screen.PREVIEW
            logger.bind(
                root=str(self.state.root),
                entries=len(entries),
                moves=len(plan.to_execute()),
                skipped=len(plan.skipped()),
                component="controller",
            ).info("scan: completed")
        except Exception as exc:
            logger.bind(
                root=str(self.state.root),
                error_type=type(exc).__name__,
                component="controller",
            ).exception("scan: failed")
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
        plan = self.state.plan
        logger.bind(
            root=str(plan.root),
            moves=len(plan.to_execute()),
            component="controller",
        ).info("organize: started")
        try:
            result = self.state.service.execute(plan)
            self.state.result = result
            self.state.screen = Screen.RESULTS
            logger.bind(
                root=str(plan.root),
                moved=len(result.succeeded) - len(result.failures),
                failed=len(result.failures),
                component="controller",
            ).info("organize: completed")
        except Exception as exc:
            logger.bind(
                root=str(plan.root),
                error_type=type(exc).__name__,
                component="controller",
            ).exception("organize: failed")
            self.state.error = f"Could not organize: {exc}"
        finally:
            self.state.loading = False
        self.render()

    def back_home(self) -> None:
        logger.bind(component="controller").info("back_home")
        self.state.screen = Screen.HOME
        self.state.plan = None
        self.state.entries = ()
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
