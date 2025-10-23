"""High-level controller orchestrating LinkedIn authentication."""
from __future__ import annotations

from typing import Optional

from .browser import LinkedInBrowserController
from ..models.session import Credentials, SessionManager


class LinkedInLoginController:
    """Encapsulate the steps required to authenticate on LinkedIn."""

    ENTRY_URL = "https://www.linkedin.com/"
    DEFAULT_HOME_URL = "https://www.linkedin.com/feed/"

    def __init__(self, browser: LinkedInBrowserController, session_manager: SessionManager) -> None:
        self._browser = browser
        self._sessions = session_manager

    # -- credential helpers -------------------------------------------------
    def get_credentials(self) -> Optional[Credentials]:
        """Return stored credentials, if any."""

        return self._sessions.get_credentials()

    def save_credentials(self, email: str, password: str) -> Credentials:
        """Persist credentials and return the stored value."""

        return self._sessions.save_credentials(email, password)

    # -- browser operations -------------------------------------------------
    def open_home(self, url: Optional[str] = None):
        """Open LinkedIn using the persisted Playwright context."""

        target = url or self.DEFAULT_HOME_URL
        return self._browser.open_page(target)

    def login_with_credentials(self, credentials: Credentials):
        """Trigger the LinkedIn login flow using the provided credentials."""

        return self._browser.login_with_credentials(credentials.email, credentials.password)

    def mark_initialized(self, login_url: Optional[str]) -> None:
        """Persist information indicating the login has been completed at least once."""

        self._sessions.mark_initialized(login_url or self.DEFAULT_HOME_URL)

    def status(self):
        """Proxy to the session manager status helper."""

        return self._sessions.status()


__all__ = ["LinkedInLoginController"]
