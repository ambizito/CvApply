"""Screen dedicated to the first Playwright onboarding."""
from __future__ import annotations

import threading
import tkinter as tk
from typing import Callable

from tkinter import messagebox, ttk

from ..playwright_controller import PlaywrightController
from ..session_manager import SessionManager
from ..system_checks import LinkedInAccessCheck
from .base import BaseScreen


class OnboardingScreen(BaseScreen):
    def __init__(
        self,
        parent: tk.Widget,
        router,
        app_state,
        tokens,
        controller: PlaywrightController,
        session_manager: SessionManager,
        *,
        on_initialized: Callable[[], None],
    ) -> None:
        super().__init__(parent, router, app_state, tokens)
        self.controller = controller
        self.session_manager = session_manager
        self.on_initialized = on_initialized

    def build(self) -> None:
        ttk.Label(self, text="Primeiro acesso", style="Heading.TLabel").pack(
            anchor=tk.W, pady=(0, self.tokens.spacing.inline)
        )

        ttk.Label(
            self,
            text=(
                "Vamos configurar sua sessão local. Clique em \"Abrir navegador\" para realizar o login "
                "manualmente. Quando finalizar, feche o navegador e clique em \"Confirmar login\"."
            ),
            wraplength=620,
            justify=tk.LEFT,
        ).pack(anchor=tk.W)

        form = ttk.Frame(self)
        form.pack(fill=tk.X, pady=(self.tokens.spacing.section, 0))
        ttk.Label(form, text="URL de login").pack(anchor=tk.W)
        status = self.app_state.session_status
        self.login_url_var = tk.StringVar(value=status.login_url or "https://www.linkedin.com")
        ttk.Entry(form, textvariable=self.login_url_var).pack(fill=tk.X)

        actions = ttk.Frame(self)
        actions.pack(fill=tk.X, pady=(self.tokens.spacing.section, 0))

        ttk.Button(actions, text="Abrir navegador", command=self._open_browser, style="Accent.TButton").pack(
            side=tk.LEFT
        )
        self.confirm_button = ttk.Button(
            actions, text="Confirmar login", command=self._confirm_login, state=tk.DISABLED
        )
        self.confirm_button.pack(side=tk.LEFT, padx=(self.tokens.spacing.inline, 0))

    def on_show(self, **params: object) -> None:
        self.confirm_button.config(state=tk.DISABLED)
        status = self.app_state.session_status
        if status.login_url:
            self.login_url_var.set(status.login_url)

    def _open_browser(self) -> None:
        url = self.login_url_var.get().strip()
        if not url:
            messagebox.showerror("URL inválida", "Informe uma URL para iniciar o login.")
            return

        check = LinkedInAccessCheck()
        result = check.run()
        if not result.success:
            messagebox.showerror("Falha de acesso ao LinkedIn", result.details)
            return

        future = self.controller.open_login(url)

        def _wait_for_open() -> None:
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: messagebox.showerror("Erro ao abrir navegador", str(exc)))
                return

            self.after(0, self._detect_login_fields)

        threading.Thread(target=_wait_for_open, daemon=True).start()

    def _detect_login_fields(self) -> None:
        cred_window = tk.Toplevel(self)
        cred_window.title("Preencher credenciais LinkedIn")
        cred_window.geometry("350x200")
        cred_window.resizable(False, False)

        ttk.Label(cred_window, text="Email:").pack(pady=(20, 0))
        email_var = tk.StringVar()
        ttk.Entry(cred_window, textvariable=email_var).pack()

        ttk.Label(cred_window, text="Senha:").pack(pady=(10, 0))
        senha_var = tk.StringVar()
        ttk.Entry(cred_window, textvariable=senha_var, show="*").pack()

        def submit() -> None:
            email = email_var.get().strip()
            senha = senha_var.get().strip()
            if not email or not senha:
                messagebox.showerror("Erro", "Preencha email e senha.")
                return
            cred_window.destroy()
            self._fill_login_fields(email, senha)

        ttk.Button(cred_window, text="Entrar", command=submit).pack(pady=(20, 0))

    def _fill_login_fields(self, email: str, senha: str) -> None:
        try:
            # Placeholder for future automation
            messagebox.showinfo("Login", "Credenciais enviadas para o LinkedIn. (Automação a implementar)")
            self.confirm_button.config(state=tk.NORMAL)
        except Exception as exc:  # pragma: no cover - defensive
            messagebox.showerror("Erro de automação", str(exc))

    def _confirm_login(self) -> None:
        try:
            self.controller.close_browser()
        except Exception as exc:  # noqa: BLE001
            messagebox.showwarning("Aviso", f"Não foi possível fechar o navegador automaticamente: {exc}")

        self.session_manager.mark_initialized(self.login_url_var.get().strip())
        messagebox.showinfo(
            "Sessão salva",
            "Configuração inicial concluída. Na próxima execução abriremos diretamente o painel principal.",
        )
        self.confirm_button.config(state=tk.DISABLED)
        self.on_initialized()
