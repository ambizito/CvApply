"""Minimal fallback implementation of the requests API for offline tests."""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, Optional
from urllib import error, request

from .exceptions import RequestException


@dataclass
class Response:
    """Simplified HTTP response object."""

    url: str
    status_code: int
    text: str

    def raise_for_status(self) -> None:
        if self.status_code >= 400:
            raise RequestException(f"HTTP error {self.status_code} for {self.url}")


def get(url: str, timeout: Optional[float] = None, **kwargs: Dict[str, Any]) -> Response:
    """Perform a very small subset of requests.get using urllib."""

    req = request.Request(url, method="GET")
    try:
        with request.urlopen(req, timeout=timeout) as resp:  # type: ignore[call-arg]
            body = resp.read().decode("utf-8", errors="replace")
            status = getattr(resp, "status", 200)
            return Response(url=url, status_code=status, text=body)
    except error.URLError as exc:  # pragma: no cover - network failures
        raise RequestException(str(exc)) from exc


__all__ = ["RequestException", "Response", "get"]
