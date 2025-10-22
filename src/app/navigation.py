"""Navigation primitives for the Tkinter application."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Dict, Optional, Protocol

import tkinter as tk
from tkinter import ttk

from .session_manager import SessionStatus
from .ui_vars import UITokens


class ScreenFactory(Protocol):
    """Callable that returns a screen instance."""

    def __call__(
        self,
        parent: tk.Widget,
        router: NavigationController,
        app_state: AppState,
        tokens: UITokens,
    ) -> "BaseScreen":
        ...


@dataclass
class AppState:
    """Shared application state injected into screens."""

    session_status: SessionStatus
    current_user: Optional[str] = None

    def update_status(self, status: SessionStatus) -> None:
        """Update the tracked session status and user information."""

        self.session_status = status
        self.current_user = status.email or self.current_user


@dataclass
class _ScreenRegistration:
    factory: ScreenFactory
    instance: Optional["BaseScreen"] = None


class NavigationController:
    """Simple router that handles screen instantiation and switching."""

    def __init__(self, container: ttk.Frame, app_state: AppState, tokens: UITokens) -> None:
        self.container = container
        self.app_state = app_state
        self.tokens = tokens
        self._screens: Dict[str, _ScreenRegistration] = {}
        self._current: Optional["BaseScreen"] = None

    def register(self, name: str, factory: ScreenFactory) -> None:
        """Register a screen factory for later use."""

        if name in self._screens:
            raise ValueError(f"Screen '{name}' already registered")
        self._screens[name] = _ScreenRegistration(factory=factory)

    def show(self, name: str, **params: object) -> None:
        """Display a screen by name, instantiating it lazily."""

        if name not in self._screens:
            valid = ", ".join(sorted(self._screens)) or "<none>"
            raise KeyError(f"Screen '{name}' not registered. Available: {valid}")

        registration = self._screens[name]
        if registration.instance is None:
            registration.instance = registration.factory(self.container, self, self.app_state, self.tokens)
            registration.instance.build()

        if self._current is not registration.instance:
            if self._current is not None:
                self._current.pack_forget()
            registration.instance.pack(fill=tk.BOTH, expand=True)
            self._current = registration.instance

        registration.instance.on_show(**params)

    def current_screen(self) -> Optional["BaseScreen"]:
        """Return the currently displayed screen."""

        return self._current


from .screens.base import BaseScreen  # noqa: E402  # isort:skip
