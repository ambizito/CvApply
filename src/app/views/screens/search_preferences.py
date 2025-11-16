"""Screen that allows configuring LinkedIn job search filters."""
from __future__ import annotations

import tkinter as tk
from tkinter import ttk

from ...models import (
    ALLOWED_DATE_FILTERS,
    ALLOWED_EXPERIENCE_LEVELS,
    SearchPreferences,
    SearchPreferencesRepository,
)
from .base import BaseScreen


class SearchPreferencesScreen(BaseScreen):
    """Form that captures search filters such as localidade e modo de trabalho."""

    PRESET_LOCATIONS = [
        "São Paulo, Brasil",
        "Natal, Brasil",
        "Brasil",
        "Gotemburgo, Suécia",
        "Suécia",
    ]

    def __init__(
        self,
        parent,
        router,
        app_state,
        tokens,
        *,
        preferences_repo: SearchPreferencesRepository,
    ) -> None:
        super().__init__(parent, router, app_state, tokens)
        self.preferences_repo = preferences_repo
        self.status_var = tk.StringVar(value="")

        prefs = self.preferences_repo.load()
        self.keyword_var = tk.StringVar(value=prefs.keywords)
        self.location_var = tk.StringVar(value=prefs.location)
        self.remote_var = tk.BooleanVar(value=prefs.remote)
        self.hybrid_var = tk.BooleanVar(value=prefs.hybrid)
        self.onsite_var = tk.BooleanVar(value=prefs.onsite)
        self.easy_apply_var = tk.BooleanVar(value=prefs.easy_apply_only)
        self.date_var = tk.StringVar(value=prefs.date_filter)
        self.experience_vars: dict[str, tk.BooleanVar] = {}
        for level in sorted(ALLOWED_EXPERIENCE_LEVELS):
            self.experience_vars[level] = tk.BooleanVar(value=level in prefs.experience_levels)
        self.companies_text = tk.Text(self, height=4, width=40, wrap="word")
        if prefs.companies:
            self.companies_text.insert("1.0", ", ".join(prefs.companies))

    def build(self) -> None:
        ttk.Label(self, text="Procurar vagas", style="Heading.TLabel").pack(
            anchor="w", pady=(0, self.tokens.spacing.inline)
        )
        ttk.Label(
            self,
            text=(
                "Ajuste os filtros de busca usados na candidatura simplificada. "
                "Para autoaplicação não supervisionada, o filtro de candidatura simplificada é obrigatório."
            ),
            style="Secondary.TLabel",
            wraplength=640,
            justify="left",
        ).pack(anchor="w")

        form = ttk.Frame(self, style="Surface.TFrame")
        form.pack(anchor="w", fill=tk.X, pady=(self.tokens.spacing.section, 0))

        self._build_keywords(form)
        self._build_location(form)
        self._build_workplace(form)
        self._build_date_filter(form)
        self._build_experience(form)
        self._build_companies(form)
        self._build_easy_apply(form)

        actions = ttk.Frame(self)
        actions.pack(anchor="w", pady=(self.tokens.spacing.section, 0))
        ttk.Button(actions, text="Salvar preferências", command=self._save_preferences, style="Accent.TButton").pack(
            side=tk.LEFT
        )
        ttk.Button(actions, text="Voltar para o início", command=lambda: self.router.show("Home")).pack(
            side=tk.LEFT, padx=(self.tokens.spacing.inline, 0)
        )

        ttk.Label(self, textvariable=self.status_var, style="Secondary.TLabel", wraplength=640, justify="left").pack(
            anchor="w", pady=(self.tokens.spacing.inline, 0)
        )

    def on_show(self, **params: object) -> None:
        self._reload_preferences()
        self.status_var.set("")

    # -- sections ---------------------------------------------------------
    def _build_keywords(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=(0, self.tokens.spacing.inline))
        ttk.Label(container, text="Palavras-chave / cargo", width=25).pack(side=tk.LEFT, anchor="w")
        ttk.Entry(container, textvariable=self.keyword_var, width=50).pack(side=tk.LEFT, anchor="w")

    def _build_location(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=(0, self.tokens.spacing.inline))
        ttk.Label(container, text="Localidade preferida", width=25).pack(side=tk.LEFT, anchor="w")
        ttk.Combobox(
            container,
            textvariable=self.location_var,
            values=self.PRESET_LOCATIONS,
            width=47,
        ).pack(side=tk.LEFT, anchor="w")

    def _build_workplace(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=(0, self.tokens.spacing.inline))
        ttk.Label(container, text="Modalidade", width=25).pack(side=tk.LEFT, anchor="n")
        options = ttk.Frame(container)
        options.pack(side=tk.LEFT, anchor="w")
        ttk.Checkbutton(options, text="Remoto", variable=self.remote_var).pack(anchor="w")
        ttk.Checkbutton(options, text="Híbrido", variable=self.hybrid_var).pack(anchor="w")
        ttk.Checkbutton(options, text="Presencial", variable=self.onsite_var).pack(anchor="w")

    def _build_date_filter(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=(0, self.tokens.spacing.inline))
        ttk.Label(container, text="Data do anúncio", width=25).pack(side=tk.LEFT, anchor="n")
        options = ttk.Frame(container)
        options.pack(side=tk.LEFT, anchor="w")
        for key, label in ALLOWED_DATE_FILTERS.items():
            ttk.Radiobutton(options, text=label, value=key, variable=self.date_var).pack(anchor="w")

    def _build_experience(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=(0, self.tokens.spacing.inline))
        ttk.Label(container, text="Nível de experiência", width=25).pack(side=tk.LEFT, anchor="n")
        options = ttk.Frame(container)
        options.pack(side=tk.LEFT, anchor="w")
        for level in sorted(ALLOWED_EXPERIENCE_LEVELS):
            ttk.Checkbutton(options, text=level, variable=self.experience_vars[level]).pack(anchor="w")

    def _build_companies(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=(0, self.tokens.spacing.inline))
        ttk.Label(container, text="Empresas-alvo", width=25).pack(side=tk.LEFT, anchor="n")
        self.companies_text.pack(in_=container, side=tk.LEFT, anchor="w")
        ttk.Label(
            container,
            text="Separe por vírgulas ou quebras de linha.",
            style="Secondary.TLabel",
        ).pack(side=tk.LEFT, anchor="w", padx=(self.tokens.spacing.inline, 0))

    def _build_easy_apply(self, parent: ttk.Frame) -> None:
        container = ttk.Frame(parent)
        container.pack(fill=tk.X, pady=(0, self.tokens.spacing.inline))
        ttk.Label(container, text="Candidatura", width=25).pack(side=tk.LEFT, anchor="n")
        ttk.Checkbutton(
            container,
            text="Exigir candidatura simplificada (obrigatório)",
            variable=self.easy_apply_var,
            state="disabled",
        ).pack(side=tk.LEFT, anchor="w")

    # -- actions ----------------------------------------------------------
    def _reload_preferences(self) -> None:
        prefs = self.preferences_repo.load()
        self.keyword_var.set(prefs.keywords)
        self.location_var.set(prefs.location)
        self.remote_var.set(prefs.remote)
        self.hybrid_var.set(prefs.hybrid)
        self.onsite_var.set(prefs.onsite)
        self.easy_apply_var.set(True)
        self.date_var.set(prefs.date_filter)
        for level, var in self.experience_vars.items():
            var.set(level in prefs.experience_levels)
        self.companies_text.delete("1.0", tk.END)
        if prefs.companies:
            self.companies_text.insert("1.0", ", ".join(prefs.companies))

    def _save_preferences(self) -> None:
        experience_levels = [level for level, var in self.experience_vars.items() if var.get()]
        companies = self._parse_companies(self.companies_text.get("1.0", tk.END))
        preferences = SearchPreferences(
            keywords=self.keyword_var.get(),
            location=self.location_var.get(),
            remote=self.remote_var.get(),
            hybrid=self.hybrid_var.get(),
            onsite=self.onsite_var.get(),
            date_filter=self.date_var.get(),
            experience_levels=experience_levels,
            companies=companies,
            easy_apply_only=True,
        )
        saved = self.preferences_repo.save(preferences)
        summary = self._format_summary(saved)
        self.status_var.set(f"Preferências salvas: {summary}")
        self.show_message("Preferências atualizadas", "Filtros de busca salvos com sucesso.")

    def _parse_companies(self, raw: str) -> list[str]:
        chunks = [chunk.strip() for chunk in raw.replace("\n", ",").split(",")]
        return [chunk for chunk in chunks if chunk]

    def _format_summary(self, prefs: SearchPreferences) -> str:
        modalities = [
            label
            for label, selected in [
                ("Remoto", prefs.remote),
                ("Híbrido", prefs.hybrid),
                ("Presencial", prefs.onsite),
            ]
            if selected
        ]
        location = prefs.location or "qualquer região"
        mode_text = ", ".join(modalities) if modalities else "qualquer modalidade"
        return f"{prefs.keywords or 'qualquer cargo'} em {location} ({mode_text})"


__all__ = ["SearchPreferencesScreen"]
