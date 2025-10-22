"""Placeholder home screen displayed after the onboarding."""
from __future__ import annotations

from tkinter import ttk

from .base import BaseScreen


class HomeScreen(BaseScreen):
    """Simple placeholder for the home/dashboard screen."""

    def build(self) -> None:
        ttk.Label(self, text="Página inicial", style="Heading.TLabel").pack(
            anchor="w", pady=(0, self.tokens.spacing.inline)
        )

        ttk.Button(
            self,
            text="Abrir LinkedIn novamente",
            command=self._open_linkedin,
            style="Accent.TButton",
        ).pack(anchor="w", pady=(self.tokens.spacing.section, 0))

        ttk.Button(
            self,
            text="Redigir carta de apresentação",
            command=self._compose_cover_letter,
        ).pack(anchor="w", pady=(self.tokens.spacing.inline, 0))

        ttk.Button(
            self,
            text="Preparar email de candidatura",
            command=self._draft_application_email,
        ).pack(anchor="w", pady=(self.tokens.spacing.inline, 0))

        self.message_label = ttk.Label(self, wraplength=620, justify="left", style="Secondary.TLabel")
        self.message_label.pack(anchor="w", pady=(self.tokens.spacing.section, 0))

    def on_show(self, **params: object) -> None:
        email_display = self.app_state.session_status.email or "usuário"
        message = (
            f"Bem-vindo(a), {email_display}! Se o navegador estiver aberto com sua conta, você já pode continuar "
            "as próximas etapas do CvApply."
        )
        self.message_label.config(text=message)

    def _open_linkedin(self) -> None:
        self.show_message(
            "Em desenvolvimento",
            "A navegação completa do painel será implementada nas próximas etapas.",
        )

    def _compose_cover_letter(self) -> None:
        self.show_message(
            "Em desenvolvimento",
            "A redação assistida de cartas de apresentação será adicionada futuramente.",
        )

    def _draft_application_email(self) -> None:
        self.show_message(
            "Em desenvolvimento",
            "O assistente para montar emails de candidatura será implementado nas próximas etapas.",
        )
