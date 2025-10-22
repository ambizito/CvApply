"""Screen responsible for running environment checks."""
from __future__ import annotations

import threading
import tkinter as tk
from typing import Callable, List

from tkinter import ttk

from ..system_checks import SystemCheckResult, SystemTestRunner
from .base import BaseScreen


class PreflightScreen(BaseScreen):
    """Execute initial system checks before onboarding/login flows."""

    def __init__(
        self,
        parent: tk.Widget,
        router,
        app_state,
        tokens,
        runner: SystemTestRunner,
        *,
        on_success: Callable[[], None],
        on_missing_credentials: Callable[[], None],
    ) -> None:
        super().__init__(parent, router, app_state, tokens)
        self.runner = runner
        self.on_success = on_success
        self.on_missing_credentials = on_missing_credentials
        self._is_running = False
        self._current_checks: List[str] = []
        self._result_vars: List[tk.StringVar] = []

    def build(self) -> None:
        title = ttk.Label(self, text="Preparação do ambiente", style="Heading.TLabel")
        title.pack(anchor=tk.W, pady=(0, self.tokens.spacing.inline))

        description = (
            "Antes de continuar, validaremos a conexão com a internet, o acesso ao LinkedIn "
            "e a disponibilidade das credenciais salvas."
        )
        ttk.Label(self, text=description, wraplength=620, justify=tk.LEFT).pack(anchor=tk.W)

        self.status_var = tk.StringVar(value="Executando verificações iniciais...")
        ttk.Label(self, textvariable=self.status_var).pack(anchor=tk.W, pady=(self.tokens.spacing.section, 4))

        self.list_frame = ttk.Frame(self)
        self.list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, self.tokens.spacing.section))

        self.retry_button = ttk.Button(self, text="Tentar novamente", command=self._start_checks)
        self.retry_button.pack(anchor=tk.W)
        self.retry_button.config(state=tk.DISABLED)

    def on_show(self, **params: object) -> None:
        self.after(100, self._start_checks)

    def _prepare_rows(self) -> None:
        checks = self.runner.get_checks()
        self._current_checks = [check.name for check in checks]
        for child in self.list_frame.winfo_children():
            child.destroy()
        self._result_vars.clear()
        for name in self._current_checks:
            var = tk.StringVar(value=f"{name}: aguardando...")
            self._result_vars.append(var)
            ttk.Label(self.list_frame, textvariable=var, wraplength=620, justify=tk.LEFT).pack(anchor=tk.W, pady=2)

    def _start_checks(self) -> None:
        if self._is_running:
            return
        self._is_running = True
        self.retry_button.config(state=tk.DISABLED)
        self.status_var.set("Executando verificações iniciais...")
        self._prepare_rows()
        checks = self.runner.get_checks()

        def _worker() -> None:
            results: List[SystemCheckResult] = []
            for index, check in enumerate(checks):
                result = check.run()
                results.append(result)
                self.after(0, lambda idx=index, res=result: self._update_result(idx, res))
            self.after(0, lambda: self._finish(results))

        threading.Thread(target=_worker, daemon=True).start()

    def _update_result(self, index: int, result: SystemCheckResult) -> None:
        status_text = "OK" if result.success else "Falha"
        details = f" - {result.details}" if result.details else ""
        if index < len(self._result_vars):
            self._result_vars[index].set(f"{self._current_checks[index]}: {status_text}{details}")

    def _finish(self, results: List[SystemCheckResult]) -> None:
        self._is_running = False
        cred_check = next((r for r in results if r.name == "Credenciais disponíveis"), None)
        if all(result.success for result in results):
            self.status_var.set("Todas as verificações foram concluídas com sucesso.")
            self.after(200, self.on_success)
        elif cred_check and not cred_check.success:
            self.status_var.set("Credenciais não encontradas. Por favor, cadastre suas credenciais do LinkedIn.")
            self.after(200, self.on_missing_credentials)
        else:
            self.status_var.set(
                "Algumas verificações falharam. Ajuste o ambiente ou corrija as credenciais e tente novamente."
            )
            self.retry_button.config(state=tk.NORMAL)
