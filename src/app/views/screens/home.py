"""Home screen providing shortcuts for LinkedIn automations."""
from __future__ import annotations

import threading
import tkinter as tk
from typing import Any, Callable

from tkinter import ttk

from ...controllers import LinkedInActionsController
from ...models.scrap_user import ScrapUserRepository
from .base import BaseScreen


class HomeScreen(BaseScreen):
    """Dashboard that orchestrates LinkedIn navigation features."""

    def __init__(
        self,
        parent,
        router,
        app_state,
        tokens,
        *,
        actions_controller: LinkedInActionsController,
        scrap_repository: ScrapUserRepository,
    ) -> None:
        super().__init__(parent, router, app_state, tokens)
        self.actions_controller = actions_controller
        self.scrap_repository = scrap_repository
        self.status_var = tk.StringVar(value="")
        self.profile_text: tk.Text | None = None
        self.description_label: ttk.Label | None = None
        self.message_label: ttk.Label | None = None
        self.status_label: ttk.Label | None = None
        self._auto_scan_started = False

    def build(self) -> None:
        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Página inicial", style="Heading.TLabel").grid(
            row=0, column=0, sticky="w", pady=(0, self.tokens.spacing.inline)
        )

        self.description_label = ttk.Label(
            self,
            text=(
                "Este painel oferece atalhos para navegar nas vagas e revisar o perfil. "
                "O nome do candidato será verificado automaticamente ao iniciar o aplicativo."
            ),
            style="Secondary.TLabel",
            wraplength=self._calculate_wraplength(),
            justify="left",
        )
        self.description_label.grid(row=1, column=0, sticky="we")

        button_frame = ttk.Frame(self)
        button_frame.grid(row=2, column=0, sticky="w", pady=(self.tokens.spacing.section, 0))
        button_frame.columnconfigure(0, weight=1)

        ttk.Button(
            button_frame,
            text="Abrir página de vagas",
            command=self._open_jobs_page,
            style="Accent.TButton",
        ).grid(row=0, column=0, sticky="w")

        ttk.Button(
            button_frame,
            text="Procurar vagas",
            command=self._open_job_preferences,
        ).grid(row=1, column=0, sticky="w", pady=(self.tokens.spacing.inline, 0))

        ttk.Button(
            button_frame,
            text="Abrir meu perfil",
            command=self._open_profile_page,
        ).grid(row=2, column=0, sticky="w", pady=(self.tokens.spacing.inline, 0))

        self.message_label = ttk.Label(
            self, wraplength=self._calculate_wraplength(), justify="left", style="Secondary.TLabel"
        )
        self.message_label.grid(row=3, column=0, sticky="we", pady=(self.tokens.spacing.section, 0))

        self.status_label = ttk.Label(
            self,
            textvariable=self.status_var,
            wraplength=self._calculate_wraplength(),
            justify="left",
            style="Secondary.TLabel",
        )
        self.status_label.grid(row=4, column=0, sticky="we", pady=(self.tokens.spacing.inline, 0))

        profile_frame = ttk.LabelFrame(self, text="Resumo do perfil do candidato")
        profile_frame.grid(
            row=5,
            column=0,
            sticky="nsew",
            pady=(self.tokens.spacing.section, 0),
            ipadx=self.tokens.spacing.inline,
            ipady=self.tokens.spacing.inline,
        )
        self.rowconfigure(5, weight=1)
        profile_frame.rowconfigure(0, weight=1)
        profile_frame.columnconfigure(0, weight=1)

        self.profile_text = tk.Text(
            profile_frame,
            height=12,
            width=80,
            wrap="word",
            state="disabled",
            relief="flat",
        )
        self.profile_text.grid(row=0, column=0, sticky="nsew")

        self.bind("<Configure>", self._on_resize)

    def on_show(self, **params: object) -> None:
        email_display = self.app_state.session_status.email or "usuário"
        message = (
            f"Bem-vindo(a), {email_display}! Se o navegador estiver aberto com sua conta, você já pode continuar "
            "as próximas etapas do CvApply."
        )
        self.message_label.config(text=message)
        self.status_var.set("")
        self._refresh_profile_summary()
        self._ensure_profile_data()

    # -- LinkedIn automations ---------------------------------------------
    def _open_jobs_page(self) -> None:
        self._run_async_action(
            start_message="Abrindo a página de vagas do LinkedIn...",
            future_factory=self.actions_controller.open_jobs_page,
            success_message=lambda url: f"Página de vagas aberta com sucesso: {url}",
        )

    def _open_profile_page(self) -> None:
        self._run_async_action(
            start_message="Abrindo o perfil do LinkedIn...",
            future_factory=self.actions_controller.open_profile_page,
            success_message=lambda url: f"Perfil aberto com sucesso: {url}",
        )

    def _scan_profile(self) -> None:
        self._run_async_action(
            start_message="Executando varredura completa do perfil...",
            future_factory=self.actions_controller.scan_profile,
            success_message=self._format_scan_message,
        )

    def _open_job_preferences(self) -> None:
        self.router.show("JobPreferences")

    # -- async helpers -----------------------------------------------------
    def _run_async_action(
        self,
        *,
        start_message: str,
        future_factory: Callable[[], Any],
        success_message: Callable[[Any], str],
    ) -> None:
        self.status_var.set(start_message)
        future = future_factory()

        def _worker() -> None:
            try:
                result = future.result()
            except Exception as exc:  # noqa: BLE001
                self.after(0, lambda: self._on_action_error(exc))
            else:
                message = success_message(result)
                self.after(0, lambda: self._on_action_success(message))

        threading.Thread(target=_worker, daemon=True).start()

    def _on_action_success(self, message: str) -> None:
        self._auto_scan_started = False
        self.status_var.set(message)
        self._refresh_profile_summary()
        self.show_message("Automação concluída", message)

    def _on_action_error(self, exc: Exception) -> None:
        self._auto_scan_started = False
        message = f"Falha ao executar a automação: {exc}"
        self.status_var.set(message)
        self.show_message("Erro na automação", message, error=True)

    def _ensure_profile_data(self) -> None:
        if self._auto_scan_started:
            return
        payload = self.scrap_repository.load()
        nome = payload.get("Nome", [])
        if nome and any(nome):
            return

        self._auto_scan_started = True
        self._run_async_action(
            start_message="Verificando perfil para identificar seu nome...",
            future_factory=self.actions_controller.scan_profile,
            success_message=lambda data: self._format_scan_message(data, automatic=True),
        )

    def _format_scan_message(self, payload: dict[str, list[Any]], automatic: bool = False) -> str:
        experiencias = payload.get("Experiência", [])
        formacao = payload.get("Formação", [])
        competencias = payload.get("Competências", [])
        prefix = "Varredura automática concluída. " if automatic else "Varredura concluída. "
        return (
            prefix
            + f"Experiências registradas: {len(experiencias)}. "
            + f"Formações registradas: {len(formacao)}. "
            + f"Competências registradas: {len(competencias)}."
        )

    def _refresh_profile_summary(self) -> None:
        if self.profile_text is None:
            return
        payload = self.scrap_repository.load()
        lines: list[str] = []

        nome = payload.get("Nome", [])
        lines.append("Nome: " + (nome[0] if nome else "não identificado"))

        def _append_section(title: str, values: list[Any]) -> None:
            lines.append("")
            lines.append(title + ":")
            if not values:
                lines.append("  - Nenhum registro disponível")
                return
            for value in values:
                if isinstance(value, dict):
                    description = "; ".join(
                        f"{key}: {val}" for key, val in value.items() if val
                    )
                    lines.append("  - " + (description or "Registro sem detalhes"))
                else:
                    lines.append("  - " + str(value))

        _append_section("Experiências", payload.get("Experiência", []))
        _append_section("Formação", payload.get("Formação", []))
        _append_section("Licenças e certificados", payload.get("Licenças e certificados", []))
        _append_section("Projetos", payload.get("Projetos", []))
        _append_section("Competências", payload.get("Competências", []))
        _append_section("Recomendações", payload.get("Recomendações", []))
        _append_section("Publicações", payload.get("Publicações", []))

        text_content = "\n".join(lines)
        self.profile_text.configure(state="normal")
        self.profile_text.delete("1.0", tk.END)
        self.profile_text.insert(tk.END, text_content)
        self.profile_text.configure(state="disabled")

    def _calculate_wraplength(self, width: int | None = None) -> int:
        available_width = width if width is not None else self.winfo_width()
        if not available_width:
            available_width = 720
        padding = self.tokens.spacing.section * 2
        return max(available_width - padding, 320)

    def _on_resize(self, event: tk.Event) -> None:  # type: ignore[override]
        wraplength = self._calculate_wraplength(event.width)
        for label in (self.description_label, self.message_label, self.status_label):
            if label is not None:
                label.configure(wraplength=wraplength)
