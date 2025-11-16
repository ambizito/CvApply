"""Persistable preferences for LinkedIn job searches."""
from __future__ import annotations

import json
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Iterable, List


ALLOWED_EXPERIENCE_LEVELS = {
    "Estágio",
    "Assistente",
    "Júnior",
    "Pleno-sênior",
    "Diretor",
    "Executivo",
}

ALLOWED_DATE_FILTERS = {
    "any": "A qualquer momento",
    "last_month": "Último mês",
    "last_week": "Última semana",
    "last_day": "Últimas 24 horas",
}


@dataclass(slots=True)
class SearchPreferences:
    """Structured representation of the LinkedIn search filters the user selects."""

    keywords: str = ""
    location: str = ""
    remote: bool = False
    hybrid: bool = False
    onsite: bool = False
    date_filter: str = "any"
    experience_levels: List[str] = field(default_factory=list)
    companies: List[str] = field(default_factory=list)
    easy_apply_only: bool = True

    @classmethod
    def from_dict(cls, raw: dict[str, object] | None) -> "SearchPreferences":
        if not raw:
            return cls()

        def _list(key: str) -> List[str]:
            values = raw.get(key, [])
            if isinstance(values, list):
                return [str(value) for value in values if isinstance(value, (str, int, float))]
            return []

        return cls(
            keywords=str(raw.get("keywords", "")),
            location=str(raw.get("location", "")),
            remote=bool(raw.get("remote", False)),
            hybrid=bool(raw.get("hybrid", False)),
            onsite=bool(raw.get("onsite", False)),
            date_filter=str(raw.get("date_filter", "any")),
            experience_levels=_list("experience_levels"),
            companies=_list("companies"),
            easy_apply_only=bool(raw.get("easy_apply_only", True)),
        )

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


class SearchPreferencesRepository:
    """Load and save search preferences to a JSON file."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.storage_dir / "search_preferences.json"

    def load(self) -> SearchPreferences:
        if not self.file_path.exists():
            return SearchPreferences()

        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return SearchPreferences()

        prefs = SearchPreferences.from_dict(raw if isinstance(raw, dict) else None)
        return self._normalise(prefs)

    def save(self, preferences: SearchPreferences) -> SearchPreferences:
        normalised = self._normalise(preferences)
        self.file_path.write_text(
            json.dumps(normalised.to_dict(), ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return normalised

    def _normalise(self, preferences: SearchPreferences) -> SearchPreferences:
        def _clean_list(values: Iterable[str], allowed: set[str] | None = None) -> List[str]:
            cleaned = []
            seen = set[str]()
            for value in values:
                text = str(value).strip()
                if not text:
                    continue
                if allowed is not None and text not in allowed:
                    continue
                if text.lower() in seen:
                    continue
                cleaned.append(text)
                seen.add(text.lower())
            return cleaned

        date_filter = preferences.date_filter if preferences.date_filter in ALLOWED_DATE_FILTERS else "any"

        return SearchPreferences(
            keywords=preferences.keywords.strip(),
            location=preferences.location.strip(),
            remote=bool(preferences.remote),
            hybrid=bool(preferences.hybrid),
            onsite=bool(preferences.onsite),
            date_filter=date_filter,
            experience_levels=_clean_list(preferences.experience_levels, ALLOWED_EXPERIENCE_LEVELS),
            companies=_clean_list(preferences.companies),
            # Easy Apply é obrigatório para autoaplicação não supervisionada.
            easy_apply_only=True,
        )


__all__ = [
    "SearchPreferences",
    "SearchPreferencesRepository",
    "ALLOWED_DATE_FILTERS",
    "ALLOWED_EXPERIENCE_LEVELS",
]
