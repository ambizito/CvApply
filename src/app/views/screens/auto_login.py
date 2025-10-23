"""Screen that attempts to reuse a stored LinkedIn session."""
from __future__ import annotations

import threading
import tkinter as tk
from typing import Callable, Optional

from tkinter import ttk

from ...controllers.login import LinkedInLoginController
from .base import BaseScreen


class AutoLoginScreen(BaseScreen):
    """Attempt to reuse stored session and open the LinkedIn home automatically."""

    def __init__(
        self,
        parent: tk.Widget,
        router,
        app_state,
        tokens,
        login_controller: LinkedInLoginController,
        *,
        on_completed: Callable[[], None],
    ) -> None:
        super().__init__(parent, router, app_state, tokens)
        self.login_controller = login_controller
        self.on_completed = on_completed
        self._is_running = False

    def build(self) -> None:
        ttk.Label(self, text="Login automático", style="Heading.TLabel").pack(
            anchor=tk.W, pady=(0, self.tokens.spacing.inline)
        )

        description = (
            "Vamos reutilizar a sessão salva ou realizar o primeiro acesso automaticamente ao LinkedIn."
        )
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

        credentials = self.login_controller.get_credentials()
        if credentials is None:
            self.status_var.set("Credenciais não cadastradas. Cadastre-as antes de continuar.")
            self.retry_button.config(state=tk.DISABLED)
            return

        self._is_running = True
        self.retry_button.config(state=tk.DISABLED)

        status = self.app_state.session_status
        first_login = not status.initialized

        if first_login:
            self.status_var.set("Realizando login inicial no LinkedIn...")
            future = self.login_controller.login_with_credentials(credentials)
        else:
            self.status_var.set("Reutilizando sessão salva do LinkedIn...")
            future = self.login_controller.open_home(status.login_url)

        def _worker() -> None:
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._on_failure(exc))
            else:
                self.after(0, lambda: self._on_success(result, first_login))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_success(self, result: Optional[str], first_login: bool) -> None:
        self._is_running = False
        if first_login:
            self.login_controller.mark_initialized(result if isinstance(result, str) else None)
            self.app_state.update_status(self.login_controller.status())
            self.status_var.set("Login inicial concluído e sessão salva. O LinkedIn está aberto.")
        else:
            self.status_var.set("Sessão reutilizada com sucesso. O LinkedIn está aberto.")
        self.on_completed()

    def _on_failure(self, exc: Exception) -> None:
        self._is_running = False
        self.status_var.set(f"Falha ao abrir o LinkedIn automaticamente: {exc}")
        self.retry_button.config(state=tk.NORMAL)
