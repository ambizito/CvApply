"""Lightweight fallback for the requests.exceptions namespace."""
from __future__ import annotations


class RequestException(Exception):
    """Base exception emulating requests.exceptions.RequestException."""


__all__ = ["RequestException"]
