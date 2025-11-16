"""Tkinter GUI entry point wired to the modular navigation stack."""
from __future__ import annotations

import tkinter as tk
from pathlib import Path
from tkinter import ttk

from ..controllers import LinkedInActionsController
from ..controllers.browser import LinkedInBrowserController
from ..controllers.login import LinkedInLoginController
from ..controllers.navigation import AppState, NavigationController
from ..models.scrap_user import ScrapUserRepository
from ..models.search_preferences import SearchPreferencesRepository
from ..models.session import SessionManager, SessionStatus
from ..models.system import SystemTestRunner
from ..views.screens import (
    AutoLoginScreen,
    CredentialsScreen,
    HomeScreen,
    PreflightScreen,
    SearchPreferencesScreen,
)
from ..views.theme import configure_styles


class Application(tk.Tk):
    """Tkinter application that orchestrates environment checks and login flows."""

    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self.title("CvApply - Automação LinkedIn")
        self.geometry("720x520")
        self.resizable(True, True)

        self.session_manager = SessionManager(project_root)
        initial_status = self.session_manager.status()
        self.browser = LinkedInBrowserController(initial_status.profile_dir)
        self.login_controller = LinkedInLoginController(self.browser, self.session_manager)
        self.scrap_repository = ScrapUserRepository(self.session_manager.storage_dir)
        self.search_preferences = SearchPreferencesRepository(self.session_manager.storage_dir)
        self.actions_controller = LinkedInActionsController(self.browser, self.scrap_repository)
        self.test_runner = SystemTestRunner(self.session_manager)
        self._current_status = initial_status

        self.app_state = AppState(session_status=initial_status, current_user=initial_status.email)
        self.tokens = configure_styles(self)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._container = ttk.Frame(self, padding=self.tokens.spacing.window_padding, style="TFrame")
        self._container.pack(fill=tk.BOTH, expand=True)

        self.router = NavigationController(self._container, self.app_state, self.tokens)
        self._register_screens()

        self._show_preflight()

    # region setup ---------------------------------------------------------
    def _register_screens(self) -> None:
        self.router.register(
            "Preflight",
            lambda parent, router, state, tokens: PreflightScreen(
                parent,
                router,
                state,
                tokens,
                runner=self.test_runner,
                on_success=self._advance_after_preflight,
                on_missing_credentials=lambda: self._show_credentials(self._refresh_status()),
            ),
        )
        self.router.register(
            "Credentials",
            lambda parent, router, state, tokens: CredentialsScreen(
                parent,
                router,
                state,
                tokens,
                login_controller=self.login_controller,
                on_saved=self._on_credentials_saved,
            ),
        )
        self.router.register(
            "AutoLogin",
            lambda parent, router, state, tokens: AutoLoginScreen(
                parent,
                router,
                state,
                tokens,
                login_controller=self.login_controller,
                on_completed=self._on_auto_login_completed,
            ),
        )
        self.router.register(
            "Home",
            lambda parent, router, state, tokens: HomeScreen(
                parent,
                router,
                state,
                tokens,
                actions_controller=self.actions_controller,
                scrap_repository=self.scrap_repository,
            ),
        )
        self.router.register(
            "JobPreferences",
            lambda parent, router, state, tokens: SearchPreferencesScreen(
                parent,
                router,
                state,
                tokens,
                preferences_repo=self.search_preferences,
            ),
        )

    # region state helpers -------------------------------------------------
    def _refresh_status(self) -> SessionStatus:
        status = self.session_manager.status()
        self._current_status = status
        self.app_state.update_status(status)
        return status

    # Compatibility shim ---------------------------------------------------
    def _show_preflight(self) -> None:
        self.router.show("Preflight")

    def _advance_after_preflight(self) -> None:
        status = self._refresh_status()
        if not status.has_credentials:
            self._show_credentials(status)
        else:
            self._show_auto_login(status)

    def _show_credentials(self, status: SessionStatus | None = None) -> None:
        if status is not None:
            self.app_state.update_status(status)
        self.router.show("Credentials")

    def _show_auto_login(self, status: SessionStatus | None = None) -> None:
        if status is not None:
            self.app_state.update_status(status)
        self.router.show("AutoLogin")

    def _show_home(self, status: SessionStatus | None = None) -> None:
        if status is not None:
            self.app_state.update_status(status)
        self.router.show("Home")

    # region events --------------------------------------------------------
    def _on_credentials_saved(self, _event: tk.Event | None = None) -> None:
        self._show_auto_login(self._refresh_status())

    def _on_auto_login_completed(self, _event: tk.Event | None = None) -> None:
        self._show_home(self._refresh_status())

    def _on_close(self) -> None:
        try:
            self.browser.shutdown()
        finally:
            self.destroy()


__all__ = ["Application"]
