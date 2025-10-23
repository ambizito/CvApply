"""Local persistence helpers for storing scraped LinkedIn profile data."""
from __future__ import annotations

from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Dict, Iterable, List, Sequence
import json


DEFAULT_SCRAP_TEMPLATE: Dict[str, List[Any]] = {
    "Nome": [],
    "Formação": [],
    "Experiência": [],
    "Licenças e certificados": [],
    "Projetos": [],
    "Competências": [],
    "Recomendações": [],
    "Publicações": [],
}


def _default_payload() -> Dict[str, List[Any]]:
    """Return a fresh copy of the default structure."""

    return {key: value.copy() for key, value in DEFAULT_SCRAP_TEMPLATE.items()}


def _normalise_item(item: Any) -> Any:
    """Create a hashable representation for comparison purposes."""

    if isinstance(item, dict):
        return tuple(sorted((key, _normalise_item(value)) for key, value in item.items()))
    if isinstance(item, (list, tuple)):
        return tuple(_normalise_item(value) for value in item)
    return item


def _merge_unique(existing: Sequence[Any], incoming: Iterable[Any]) -> List[Any]:
    """Return a list that combines entries without duplicating values."""

    merged: List[Any] = list(existing)
    seen = {_normalise_item(item) for item in existing}
    for item in incoming:
        if item is None:
            continue
        signature = _normalise_item(item)
        if signature in seen:
            continue
        merged.append(item)
        seen.add(signature)
    return merged


@dataclass(slots=True)
class ExperienceRecord:
    """Structured representation for a single experience entry."""

    cargo: str = ""
    empresa: str = ""
    periodo: str = ""
    local: str = ""
    descricao: str = ""

    def to_dict(self) -> Dict[str, str]:
        """Convert the record into a JSON-serialisable dictionary."""

        data = asdict(self)
        # Remove empty fields to keep the JSON concise.
        return {key: value for key, value in data.items() if value}


class ScrapUserRepository:
    """Persist and retrieve scraped LinkedIn profile data."""

    def __init__(self, storage_dir: Path) -> None:
        self.storage_dir = storage_dir
        self.storage_dir.mkdir(parents=True, exist_ok=True)
        self.file_path = self.storage_dir / "ScrapUser.json"

    def load(self) -> Dict[str, List[Any]]:
        """Return the stored payload or the default template when missing."""

        if not self.file_path.exists():
            return _default_payload()

        try:
            raw = json.loads(self.file_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            return _default_payload()

        payload: Dict[str, List[Any]] = {}
        for key, default_value in DEFAULT_SCRAP_TEMPLATE.items():
            value = raw.get(key, default_value)
            payload[key] = value if isinstance(value, list) else default_value.copy()
        return payload

    def save(self, data: Dict[str, List[Any]]) -> Dict[str, List[Any]]:
        """Persist the provided payload to disk."""

        normalised = _default_payload()
        for key, value in data.items():
            if key in normalised and isinstance(value, list):
                normalised[key] = value
        self.file_path.write_text(
            json.dumps(normalised, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )
        return normalised

    def update(
        self,
        *,
        nome: str | None = None,
        experiencias: Sequence[Dict[str, Any]] | None = None,
        formacao: Sequence[Any] | None = None,
        licencas: Sequence[Any] | None = None,
        projetos: Sequence[Any] | None = None,
        competencias: Sequence[Any] | None = None,
        recomendacoes: Sequence[Any] | None = None,
        publicacoes: Sequence[Any] | None = None,
    ) -> Dict[str, List[Any]]:
        """Update specific fields while keeping the remaining structure intact."""

        current = self.load()
        if nome is not None:
            if nome:
                # Keep only the most recent value but avoid duplicates.
                current["Nome"] = _merge_unique(current.get("Nome", []), [nome])[-1:]
            else:
                current["Nome"] = []

        def _merge(section: str, values: Sequence[Any] | None) -> None:
            if values is None:
                return
            current[section] = _merge_unique(current.get(section, []), values)

        _merge("Experiência", experiencias)
        _merge("Formação", formacao)
        _merge("Licenças e certificados", licencas)
        _merge("Projetos", projetos)
        _merge("Competências", competencias)
        _merge("Recomendações", recomendacoes)
        _merge("Publicações", publicacoes)

        return self.save(current)


__all__ = ["ExperienceRecord", "ScrapUserRepository"]
