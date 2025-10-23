from __future__ import annotations

import json
from pathlib import Path

from src.app.models.scrap_user import ExperienceRecord, ScrapUserRepository


def test_load_returns_default_structure(tmp_path: Path) -> None:
    repo = ScrapUserRepository(tmp_path)
    payload = repo.load()
    assert set(payload.keys()) == {
        "Nome",
        "Formação",
        "Experiência",
        "Licenças e certificados",
        "Projetos",
        "Competências",
        "Recomendações",
        "Publicações",
    }
    for value in payload.values():
        assert isinstance(value, list)
        assert value == []


def test_update_persists_name_and_experiences(tmp_path: Path) -> None:
    repo = ScrapUserRepository(tmp_path)
    experience = ExperienceRecord(
        cargo="Desenvolvedor",
        empresa="Empresa X",
        periodo="2020 - 2021",
        local="Remoto",
        descricao="Atuação no desenvolvimento de soluções.",
    )
    payload = repo.update(nome="Fulano", experiencias=[experience.to_dict()])

    saved = json.loads((tmp_path / "ScrapUser.json").read_text(encoding="utf-8"))

    assert payload["Nome"] == ["Fulano"]
    assert payload["Experiência"] == [experience.to_dict()]
    assert saved == payload


def test_update_skips_duplicate_entries(tmp_path: Path) -> None:
    repo = ScrapUserRepository(tmp_path)
    experience = ExperienceRecord(cargo="Dev").to_dict()
    repo.update(experiencias=[experience])
    payload = repo.update(experiencias=[experience])

    assert payload["Experiência"] == [experience]


def test_update_merges_other_sections(tmp_path: Path) -> None:
    repo = ScrapUserRepository(tmp_path)
    payload = repo.update(
        formacao=["Curso A"],
        competencias=["Python"],
    )
    payload = repo.update(
        formacao=["Curso A", "Curso B"],
        competencias=["Python", "SQL"],
        licencas=["Certificado X"],
    )

    assert payload["Formação"] == ["Curso A", "Curso B"]
    assert payload["Competências"] == ["Python", "SQL"]
    assert payload["Licenças e certificados"] == ["Certificado X"]
