"""Base classes for modular Tkinter screens."""
from __future__ import annotations

import tkinter as tk
from tkinter import messagebox, ttk

from ...controllers.navigation import AppState, NavigationController
from ..theme import UITokens


class BaseScreen(ttk.Frame):
    """Base implementation shared by all screens."""

    def __init__(
        self,
        parent: tk.Widget,
        router: NavigationController,
        app_state: AppState,
        tokens: UITokens,
        *,
        padding: int | tuple[int, int, int, int] | None = None,
    ) -> None:
        super().__init__(parent, style="Surface.TFrame")
        self.router = router
        self.app_state = app_state
        self.tokens = tokens
        if padding is None:
            padding = (tokens.spacing.section, tokens.spacing.section)
        self.configure(padding=padding)

    def build(self) -> None:
        """Create widgets for the screen."""

    def on_show(self, **params: object) -> None:
        """Hook executed whenever the screen becomes visible."""

    # Compatibility helpers -------------------------------------------------
    def show_message(self, title: str, message: str, *, error: bool = False) -> None:
        """Show a message box using a consistent style."""

        if error:
            messagebox.showerror(title, message)
        else:
            messagebox.showinfo(title, message)
