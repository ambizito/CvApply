from __future__ import annotations

import threading
import tkinter as tk
from pathlib import Path
from tkinter import messagebox, ttk
from typing import Callable, List

from .playwright_controller import PlaywrightController
from .session_manager import SessionManager, SessionStatus
from .system_checks import SystemCheckResult, SystemTestRunner


class Application(tk.Tk):
    """Tkinter application that orchestrates onboarding and validation flows."""

    def __init__(self, project_root: Path) -> None:
        super().__init__()
        self.title("CvApply - Onboarding")
        self.geometry("720x520")
        self.resizable(False, False)

        self.session_manager = SessionManager(project_root)
        initial_status = self.session_manager.status()
        self.controller = PlaywrightController(initial_status.profile_dir)
        self.test_runner = SystemTestRunner(self.session_manager)
        self._current_status = initial_status

        self.protocol("WM_DELETE_WINDOW", self._on_close)

        self._container = ttk.Frame(self, padding=24)
        self._container.pack(fill=tk.BOTH, expand=True)

        self._container.bind("<<SessionInitialized>>", self._on_session_initialized)
        self._container.bind("<<CredentialsSaved>>", self._on_credentials_saved)
        self._container.bind("<<AutoLoginCompleted>>", self._on_auto_login_completed)

        self._show_preflight()

    # region state helpers -------------------------------------------------
    def _refresh_status(self) -> SessionStatus:
        self._current_status = self.session_manager.status()
        return self._current_status

    def _clear_container(self) -> None:
        for child in self._container.winfo_children():
            child.destroy()

    # endregion ------------------------------------------------------------

    def _show_preflight(self) -> None:
        self._clear_container()
        frame = PreflightFrame(
            self._container,
            self.test_runner,
            on_success=self._advance_after_preflight,
        )
        frame.pack(fill=tk.BOTH, expand=True)

    def _advance_after_preflight(self) -> None:
        status = self._refresh_status()
        if not status.has_credentials:
            self._show_credentials(status)
        elif not status.initialized:
            self._show_onboarding(status)
        else:
            self._show_auto_login(status)

    def _show_credentials(self, status: SessionStatus) -> None:
        self._clear_container()
        frame = CredentialsFrame(self._container, self.session_manager)
        frame.pack(fill=tk.BOTH, expand=True)

    def _show_onboarding(self, status: SessionStatus) -> None:
        self._clear_container()
        frame = OnboardingFrame(self._container, self.controller, self.session_manager, status)
        frame.pack(fill=tk.BOTH, expand=True)

    def _show_auto_login(self, status: SessionStatus) -> None:
        self._clear_container()
        frame = AutoLoginFrame(self._container, self.controller, status)
        frame.pack(fill=tk.BOTH, expand=True)

    def _show_home(self, status: SessionStatus) -> None:
        self._clear_container()
        frame = HomeFrame(self._container, status)
        frame.pack(fill=tk.BOTH, expand=True)

    # region events --------------------------------------------------------
    def _on_session_initialized(self, _event: tk.Event) -> None:  # type: ignore[override]
        self._show_auto_login(self._refresh_status())

    def _on_credentials_saved(self, _event: tk.Event) -> None:  # type: ignore[override]
        self._show_onboarding(self._refresh_status())

    def _on_auto_login_completed(self, _event: tk.Event) -> None:  # type: ignore[override]
        self._show_home(self._refresh_status())

    def _on_close(self) -> None:
        try:
            self.controller.shutdown()
        finally:
            self.destroy()


class PreflightFrame(ttk.Frame):
    """Execute initial system checks before onboarding/login flows."""

    def __init__(
        self,
        parent: tk.Widget,
        runner: SystemTestRunner,
        on_success: Callable[[], None],
    ) -> None:
        super().__init__(parent)
        self.runner = runner
        self.on_success = on_success
        self._is_running = False
        self._current_checks: List[str] = []
        self._result_vars: List[tk.StringVar] = []

        title = ttk.Label(self, text="Preparação do ambiente", font=("Helvetica", 16, "bold"))
        title.pack(anchor=tk.W, pady=(0, 12))

        description = (
            "Antes de continuar, validaremos a conexão com a internet, o acesso ao LinkedIn "
            "e a disponibilidade das credenciais salvas."
        )
        ttk.Label(self, text=description, wraplength=620, justify=tk.LEFT).pack(anchor=tk.W)

        self.status_var = tk.StringVar(value="Executando verificações iniciais...")
        ttk.Label(self, textvariable=self.status_var).pack(anchor=tk.W, pady=(12, 4))

        self.list_frame = ttk.Frame(self, padding=(0, 8, 0, 0))
        self.list_frame.pack(fill=tk.BOTH, expand=True)

        self._prepare_rows()

        self.retry_button = ttk.Button(self, text="Tentar novamente", command=self._start_checks)
        self.retry_button.pack(anchor=tk.W, pady=(16, 0))
        self.retry_button.config(state=tk.DISABLED)

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
            self.after(200, lambda: self.master.event_generate("<<CredentialsSaved>>", when="tail"))
        else:
            self.status_var.set(
                "Algumas verificações falharam. Ajuste o ambiente ou corrija as credenciais e tente novamente."
            )
            self.retry_button.config(state=tk.NORMAL)


class CredentialsFrame(ttk.Frame):
    """Collect LinkedIn credentials on the first execution."""

    def __init__(self, parent: tk.Widget, session_manager: SessionManager) -> None:
        super().__init__(parent)
        self.session_manager = session_manager
        self.email_var = tk.StringVar()
        self.password_var = tk.StringVar()

        title = ttk.Label(self, text="Configuração de credenciais", font=("Helvetica", 16, "bold"))
        title.pack(anchor=tk.W, pady=(0, 12))

        ttk.Label(
            self,
            text=(
                "Informe o email e a senha do LinkedIn. Essas informações serão salvas localmente para "
                "automatizar o login nas próximas execuções."
            ),
            wraplength=620,
            justify=tk.LEFT,
        ).pack(anchor=tk.W)

        form = ttk.Frame(self, padding=(0, 16, 0, 0))
        form.pack(fill=tk.X)

        ttk.Label(form, text="Email").grid(row=0, column=0, sticky=tk.W)
        ttk.Entry(form, textvariable=self.email_var).grid(row=1, column=0, sticky=tk.EW, pady=(0, 8))

        ttk.Label(form, text="Senha").grid(row=2, column=0, sticky=tk.W)
        ttk.Entry(form, textvariable=self.password_var, show="*").grid(row=3, column=0, sticky=tk.EW)

        form.columnconfigure(0, weight=1)

        ttk.Button(self, text="Salvar credenciais", command=self._save_credentials).pack(anchor=tk.W, pady=(16, 0))

    def _save_credentials(self) -> None:
        email = self.email_var.get().strip()
        password = self.password_var.get()

        if "@" not in email:
            messagebox.showerror("Email inválido", "Informe um email válido do LinkedIn.")
            return
        if len(password) < 8:
            messagebox.showerror("Senha inválida", "A senha precisa ter pelo menos 8 caracteres.")
            return

        self.session_manager.save_credentials(email, password)
        messagebox.showinfo("Credenciais salvas", "As credenciais foram armazenadas com sucesso.")
        self.master.event_generate("<<CredentialsSaved>>", when="tail")


class OnboardingFrame(ttk.Frame):
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
        self.login_url_var = tk.StringVar(value=status.login_url or "https://www.linkedin.com")

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
        self.confirm_button = ttk.Button(
            actions, text="Confirmar login", command=self._confirm_login, state=tk.DISABLED
        )
        self.confirm_button.pack(side=tk.LEFT, padx=(12, 0))

        # Abre o navegador automaticamente na página de login do LinkedIn
        self.after(200, self._open_browser)


    def _open_browser(self) -> None:
        url = self.login_url_var.get().strip()
        if not url:
            messagebox.showerror("URL inválida", "Informe uma URL para iniciar o login.")
            return

        # Executa o teste de acesso ao LinkedIn antes de abrir o navegador
        from .system_checks import LinkedInAccessCheck
        check = LinkedInAccessCheck()
        result = check.run()
        if not result.success:
            messagebox.showerror("Falha de acesso ao LinkedIn", result.details)
            return

        # Abre o navegador e detecta campos de login
        future = self.controller.open_login(url)

        def _wait_for_open() -> None:
            try:
                future.result()
            except Exception as exc:  # noqa: BLE001
                self.after(
                    0,
                    lambda: (
                        messagebox.showerror("Erro ao abrir navegador", str(exc)),
                    ),
                )
                return

            # Após abrir, tenta detectar campos de login
            self.after(0, self._detect_login_fields)

        threading.Thread(target=_wait_for_open, daemon=True).start()

    def _detect_login_fields(self):
        # Aqui você pode implementar a lógica de detecção dos campos de login via Playwright
        # Para simplificação, vamos abrir um popup para o usuário informar email e senha
        cred_window = tk.Toplevel(self)
        cred_window.title("Preencher credenciais LinkedIn")
        cred_window.geometry("350x200")
        cred_window.resizable(False, False)

        tk.Label(cred_window, text="Email:").pack(pady=(20, 0))
        email_var = tk.StringVar()
        tk.Entry(cred_window, textvariable=email_var).pack()

        tk.Label(cred_window, text="Senha:").pack(pady=(10, 0))
        senha_var = tk.StringVar()
        tk.Entry(cred_window, textvariable=senha_var, show="*").pack()

        def submit():
            email = email_var.get().strip()
            senha = senha_var.get().strip()
            if not email or not senha:
                messagebox.showerror("Erro", "Preencha email e senha.")
                return
            cred_window.destroy()
            # Aqui você pode usar Playwright para preencher os campos de login
            self._fill_login_fields(email, senha)

        tk.Button(cred_window, text="Entrar", command=submit).pack(pady=(20, 0))

    def _fill_login_fields(self, email, senha):
        # Aqui você implementaria o preenchimento automático dos campos via Playwright
        # Exemplo simplificado (deve ser adaptado para uso real):
        try:
            # Exemplo: self.controller.fill_linkedin_login(email, senha)
            messagebox.showinfo("Login", "Credenciais enviadas para o LinkedIn. (Automação a implementar)")
            self.confirm_button.config(state=tk.NORMAL)
        except Exception as exc:
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
        self.master.event_generate("<<SessionInitialized>>", when="tail")


class AutoLoginFrame(ttk.Frame):
    """Attempt to reuse stored session and open the LinkedIn home automatically."""

    def __init__(self, parent: tk.Widget, controller: PlaywrightController, status: SessionStatus) -> None:
        super().__init__(parent)
        self.controller = controller
        self.status = status
        self._is_running = False

        title = ttk.Label(self, text="Login automático", font=("Helvetica", 16, "bold"))
        title.pack(anchor=tk.W, pady=(0, 12))

        description = (
            "Vamos reutilizar a sessão salva para abrir diretamente a página inicial do LinkedIn."
        )
        ttk.Label(self, text=description, wraplength=620, justify=tk.LEFT).pack(anchor=tk.W)

        self.status_var = tk.StringVar(value="Iniciando login automático...")
        ttk.Label(self, textvariable=self.status_var).pack(anchor=tk.W, pady=(12, 0))

        actions = ttk.Frame(self, padding=(0, 24, 0, 0))
        actions.pack(anchor=tk.W)
        self.retry_button = ttk.Button(actions, text="Tentar novamente", command=self._start_login)
        self.retry_button.pack(side=tk.LEFT)
        self.retry_button.config(state=tk.DISABLED)

        self.after(150, self._start_login)

    def _start_login(self) -> None:
        if self._is_running:
            return
        self._is_running = True
        self.retry_button.config(state=tk.DISABLED)
        self.status_var.set("Abrindo o LinkedIn com as credenciais salvas...")

        home_url = self.status.login_url or "https://www.linkedin.com/feed/"
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
        self.master.event_generate("<<AutoLoginCompleted>>", when="tail")

    def _on_failure(self, exc: Exception) -> None:
        self._is_running = False
        self.status_var.set(f"Falha ao abrir o LinkedIn automaticamente: {exc}")
        self.retry_button.config(state=tk.NORMAL)


class HomeFrame(ttk.Frame):
    """Simple placeholder for the home/dashboard screen."""

    def __init__(self, parent: tk.Widget, status: SessionStatus) -> None:
        super().__init__(parent)
        email_display = status.email or "usuário"

        title = ttk.Label(self, text="Página inicial", font=("Helvetica", 16, "bold"))
        title.pack(anchor=tk.W, pady=(0, 12))

        message = (
            f"Bem-vindo(a), {email_display}! Se o navegador estiver aberto com sua conta, você já pode continuar "
            "as próximas etapas do CvApply."
        )
        ttk.Label(self, text=message, wraplength=620, justify=tk.LEFT).pack(anchor=tk.W)

        ttk.Button(self, text="Abrir LinkedIn novamente", command=self._open_linkedin).pack(anchor=tk.W, pady=(16, 0))

        ttk.Button(
            self,
            text="Redigir carta de apresentação",
            command=self._compose_cover_letter,
        ).pack(anchor=tk.W, pady=(8, 0))

        ttk.Button(
            self,
            text="Preparar email de candidatura",
            command=self._draft_application_email,
        ).pack(anchor=tk.W, pady=(8, 0))

    def _open_linkedin(self) -> None:
        messagebox.showinfo(
            "Em desenvolvimento",
            "A navegação completa do painel será implementada nas próximas etapas.",
        )

    def _compose_cover_letter(self) -> None:
        messagebox.showinfo(
            "Em desenvolvimento",
            "A redação assistida de cartas de apresentação será adicionada futuramente.",
        )

    def _draft_application_email(self) -> None:
        messagebox.showinfo(
            "Em desenvolvimento",
            "O assistente para montar emails de candidatura será implementado nas próximas etapas.",
        )
