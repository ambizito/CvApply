from __future__ import annotations

from typing import Any

__all__ = ["Application"]


def __getattr__(name: str) -> Any:  # pragma: no cover - thin wrapper
    if name == "Application":
        from .gui import Application as _Application

        return _Application
    raise AttributeError(name)
