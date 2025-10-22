from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Optional

from dotenv import dotenv_values, set_key


@dataclass
class SessionStatus:
    """Simple value object describing the current onboarding status."""

    initialized: bool
    profile_dir: Path
    login_url: Optional[str] = None


class SessionManager:
    """Handle environment flags and persistent Playwright profile paths."""

    ENV_PROFILE_FLAG = "PROFILE_INITIALIZED"
    ENV_LOGIN_URL = "LOGIN_URL"

    def __init__(self, project_root: Path) -> None:
        self.project_root = project_root
        self.env_path = project_root / ".env"
        self.storage_dir = project_root / "storage"
        self.profile_dir = self.storage_dir / "webkit_profile"
        self.storage_dir.mkdir(exist_ok=True)

    def status(self) -> SessionStatus:
        values = dotenv_values(self.env_path) if self.env_path.exists() else {}
        initialized = (
            values.get(self.ENV_PROFILE_FLAG, "false").lower() == "true"
            and self.profile_dir.exists()
            and any(self.profile_dir.iterdir())
        )
        login_url = values.get(self.ENV_LOGIN_URL) if initialized else None
        return SessionStatus(initialized=initialized, profile_dir=self.profile_dir, login_url=login_url)

    def mark_initialized(self, login_url: str | None = None) -> None:
        """Persist a flag in the .env file indicating the onboarding has finished."""

        if not self.profile_dir.exists():
            self.profile_dir.mkdir(parents=True, exist_ok=True)

        if not self.env_path.exists():
            # Touch the file to allow set_key to operate.
            self.env_path.write_text("", encoding="utf-8")

        set_key(str(self.env_path), self.ENV_PROFILE_FLAG, "true")
        if login_url:
            set_key(str(self.env_path), self.ENV_LOGIN_URL, login_url)

    def reset(self) -> None:
        """Remove profile data and reset env flags (useful for troubleshooting)."""

        if self.profile_dir.exists():
            for child in self.profile_dir.glob("**/*"):
                if child.is_file():
                    child.unlink(missing_ok=True)
            for child_dir in sorted(
                (p for p in self.profile_dir.glob("**/*") if p.is_dir()),
                key=lambda p: len(p.parts),
                reverse=True,
            ):
                child_dir.rmdir()
            self.profile_dir.rmdir()

        if self.env_path.exists():
            current = {
                key: value
                for key, value in dotenv_values(self.env_path).items()
                if key not in {self.ENV_PROFILE_FLAG, self.ENV_LOGIN_URL}
            }
            lines = [f"{key}={value}" for key, value in current.items()]
            self.env_path.write_text("\n".join(lines), encoding="utf-8")

    def ensure_profile_dir(self) -> Path:
        self.profile_dir.mkdir(parents=True, exist_ok=True)
        return self.profile_dir

