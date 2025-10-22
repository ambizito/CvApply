"""Screen that attempts to reuse a stored LinkedIn session."""
from __future__ import annotations

import threading
import tkinter as tk
from typing import Callable

from tkinter import ttk

from ..playwright_controller import PlaywrightController
from .base import BaseScreen


class AutoLoginScreen(BaseScreen):
    """Attempt to reuse stored session and open the LinkedIn home automatically."""

    def __init__(
        self,
        parent: tk.Widget,
        router,
        app_state,
        tokens,
        controller: PlaywrightController,
        *,
        on_completed: Callable[[], None],
    ) -> None:
        super().__init__(parent, router, app_state, tokens)
        self.controller = controller
        self.on_completed = on_completed
        self._is_running = False

    def build(self) -> None:
        ttk.Label(self, text="Login automático", style="Heading.TLabel").pack(
            anchor=tk.W, pady=(0, self.tokens.spacing.inline)
        )

        description = "Vamos reutilizar a sessão salva para abrir diretamente a página inicial do LinkedIn."
        ttk.Label(self, text=description, wraplength=620, justify=tk.LEFT).pack(anchor=tk.W)

        self.status_var = tk.StringVar(value="Iniciando login automático...")
        ttk.Label(self, textvariable=self.status_var).pack(anchor=tk.W, pady=(self.tokens.spacing.section, 0))

        actions = ttk.Frame(self)
        actions.pack(anchor=tk.W, pady=(self.tokens.spacing.section, 0))
        self.retry_button = ttk.Button(actions, text="Tentar novamente", command=self._start_login)
        self.retry_button.pack(side=tk.LEFT)
        self.retry_button.config(state=tk.DISABLED)

    def on_show(self, **params: object) -> None:
        self.after(150, self._start_login)

    def _start_login(self) -> None:
        if self._is_running:
            return
        self._is_running = True
        self.retry_button.config(state=tk.DISABLED)
        self.status_var.set("Abrindo o LinkedIn com as credenciais salvas...")

        status = self.app_state.session_status
        home_url = status.login_url or "https://www.linkedin.com/feed/"
        future = self.controller.open_login(home_url)

        def _worker() -> None:
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._on_failure(exc))
            else:
                self.after(0, self._on_success)

        threading.Thread(target=_worker, daemon=True).start()

    def _on_success(self) -> None:
        self._is_running = False
        self.status_var.set("Login automático concluído. O navegador está na página inicial do LinkedIn.")
        self.on_completed()

    def _on_failure(self, exc: Exception) -> None:
        self._is_running = False
        self.status_var.set(f"Falha ao abrir o LinkedIn automaticamente: {exc}")
        self.retry_button.config(state=tk.NORMAL)
