"""Screen for collecting LinkedIn credentials."""
from __future__ import annotations

import tkinter as tk
from typing import Callable

from tkinter import ttk

from ..session_manager import SessionManager
from .base import BaseScreen


class CredentialsScreen(BaseScreen):
    """Collect LinkedIn credentials on the first execution."""

    def __init__(
        self,
        parent: tk.Widget,
        router,
        app_state,
        tokens,
        session_manager: SessionManager,
        *,
        on_saved: Callable[[], None],
    ) -> None:
        super().__init__(parent, router, app_state, tokens)
        self.session_manager = session_manager
        self.on_saved = on_saved
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()

    def build(self) -> None:
        ttk.Label(self, text="Configuração de credenciais", style="Heading.TLabel").pack(
            anchor=tk.W, pady=(0, self.tokens.spacing.inline)
        )

        ttk.Label(
            self,
            text=(
                "Informe o email e a senha do LinkedIn. Essas informações serão salvas localmente para "
                "automatizar o login nas próximas execuções."
            ),
            wraplength=620,
            justify=tk.LEFT,
        ).pack(anchor=tk.W)

        form = ttk.Frame(self)
        form.pack(fill=tk.X, pady=(self.tokens.spacing.section, 0))

        ttk.Label(form, text="Email").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(form, textvariable=self.email_var).grid(row=1, column=0, sticky=tk.EW, pady=(0, self.tokens.spacing.inline))

        ttk.Label(form, text="Senha").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(form, textvariable=self.password_var, show="*").grid(row=3, column=0, sticky=tk.EW)

        form.columnconfigure(0, weight=1)

        ttk.Button(self, text="Salvar credenciais", command=self._save_credentials, style="Accent.TButton").pack(
            anchor=tk.W, pady=(self.tokens.spacing.section, 0)
        )

    def on_show(self, **params: object) -> None:
        self.email_var.set("")
        self.password_var.set("")

    def _save_credentials(self) -> None:
        email = self.email_var.get().strip()
        password = self.password_var.get()

        if "@" not in email:
            self.show_message("Email inválido", "Informe um email válido do LinkedIn.", error=True)
            return
        if len(password) < 8:
            self.show_message("Senha inválida", "A senha precisa ter pelo menos 8 caracteres.", error=True)
            return

        self.session_manager.save_credentials(email, password)
        self.show_message("Credenciais salvas", "As credenciais foram armazenadas com sucesso.")
        self.on_saved()
