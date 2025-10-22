from __future__ import annotations

import threading
import tkinter as tk
from tkinter import ttk, messagebox
from pathlib import Path

from .playwright_controller import PlaywrightController
from .session_manager import SessionManager, SessionStatus


class Application(tk.Tk):
    """Tkinter application that orchestrates onboarding and validation flows."""

    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self.title("CvApply - Onboarding")
        self.geometry("720x480")
        self.resizable(False, False)

        self.session_manager = SessionManager(project_root)
        status = self.session_manager.status()
        self.controller = PlaywrightController(status.profile_dir)

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._container = ttk.Frame(self, padding=24)
        self._container.pack(fill=tk.BOTH, expand=True)

        self._container.bind("<<SessionInitialized>>", self._on_session_initialized)

        if status.initialized:
            self._show_validation(status)
        else:
            self._show_onboarding(status)

    def _clear_container(self) -> None:
        for child in self._container.winfo_children():
            child.destroy()

    def _show_onboarding(self, status: SessionStatus) -> None:
        self._clear_container()
        frame = OnboardingFrame(self._container, self.controller, self.session_manager)
        frame.pack(fill=tk.BOTH, expand=True)

    def _show_validation(self, status: SessionStatus) -> None:
        self._clear_container()
        frame = ValidationFrame(self._container, self.controller, self.session_manager, status)
        frame.pack(fill=tk.BOTH, expand=True)

    def _on_session_initialized(self, _event: tk.Event) -> None:  # type: ignore[override]
        status = self.session_manager.status()
        self._show_validation(status)

    def _on_close(self) -> None:
        try:
            self.controller.shutdown()
        finally:
            self.destroy()


class OnboardingFrame(ttk.Frame):
    def __init__(self, parent: tk.Widget, controller: PlaywrightController, session_manager: SessionManager) -> None:
        super().__init__(parent)
        self.controller = controller
        self.session_manager = session_manager
        self.login_url_var = tk.StringVar(value="https://example.com")

        title = ttk.Label(self, text="Primeiro acesso", font=("Helvetica", 16, "bold"))
        title.pack(anchor=tk.W, pady=(0, 12))

        ttk.Label(
            self,
            text=(
                "Vamos configurar sua sessão local. Clique em \"Abrir navegador\" para realizar o login "
                "manualmente. Quando finalizar, feche o navegador e clique em \"Confirmar login\"."
            ),
            wraplength=620,
            justify=tk.LEFT,
        ).pack(anchor=tk.W)

        form = ttk.Frame(self, padding=(0, 16, 0, 0))
        form.pack(fill=tk.X)
        ttk.Label(form, text="URL de login").pack(anchor=tk.W)
        ttk.Entry(form, textvariable=self.login_url_var).pack(fill=tk.X)

        actions = ttk.Frame(self, padding=(0, 24, 0, 0))
        actions.pack(fill=tk.X)
        self.open_button = ttk.Button(actions, text="Abrir navegador", command=self._open_browser)
        self.open_button.pack(side=tk.LEFT)
        self.confirm_button = ttk.Button(actions, text="Confirmar login", command=self._confirm_login, state=tk.DISABLED)
        self.confirm_button.pack(side=tk.LEFT, padx=(12, 0))

    def _open_browser(self) -> None:
        url = self.login_url_var.get().strip()
        if not url:
            messagebox.showerror("URL inválida", "Informe uma URL para iniciar o login.")
            return

        self.open_button.config(state=tk.DISABLED)
        future = self.controller.open_login(url)

        def _wait_for_open() -> None:
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001
                self.after(
                    0,
                    lambda: (
                        self.open_button.config(state=tk.NORMAL),
                        messagebox.showerror("Erro ao abrir navegador", str(exc)),
                    ),
                )
                return

            self.after(
                0,
                lambda: (
                    self.confirm_button.config(state=tk.NORMAL),
                    self.open_button.config(state=tk.NORMAL),
                    messagebox.showinfo(
                        "Navegador pronto",
                        "O navegador está aberto. Complete o login manualmente e, ao finalizar, feche a janela \npara continuar.",
                    ),
                ),
            )

        threading.Thread(target=_wait_for_open, daemon=True).start()

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
        self.master.event_generate("<<SessionInitialized>>", when="tail")


class ValidationFrame(ttk.Frame):
    def __init__(
        self,
        parent: tk.Widget,
        controller: PlaywrightController,
        session_manager: SessionManager,
        status: SessionStatus,
    ) -> None:
        super().__init__(parent)
        self.controller = controller
        self.session_manager = session_manager
        self.status = status

        title = ttk.Label(self, text="Verificação de sessão", font=("Helvetica", 16, "bold"))
        title.pack(anchor=tk.W, pady=(0, 12))

        self.feedback = ttk.Label(self, text="Validando sessão salva...", wraplength=620, justify=tk.LEFT)
        self.feedback.pack(anchor=tk.W)

        self.after(100, self._validate_session)

        actions = ttk.Frame(self, padding=(0, 24, 0, 0))
        actions.pack(fill=tk.X)
        ttk.Button(actions, text="Abrir navegador", command=self._open_dashboard_browser).pack(side=tk.LEFT)

    def _validate_session(self) -> None:
        def _task() -> bool:
            probe_url = self.status.login_url or "about:blank"
            return self.controller.validate_session(probe_url)

        def _update(result: bool) -> None:
            if result:
                self.feedback.config(
                    text=(
                        "Sessão carregada com sucesso! Você pode avançar para o painel principal. "
                        "(Funcionalidades serão implementadas nas próximas etapas.)"
                    )
                )
            else:
                self.feedback.config(
                    text=(
                        "Não foi possível validar a sessão salva. Utilize o menu de configurações futuras para "
                        "repetir o processo de login."
                    )
                )

        def _worker() -> None:
            result = _task()
            self.after(0, lambda: _update(result))

        threading.Thread(target=_worker, daemon=True).start()

    def _open_dashboard_browser(self) -> None:
        messagebox.showinfo(
            "Em desenvolvimento",
            "As funcionalidades de busca de vagas e preenchimento automático serão adicionadas em breve.",
        )

