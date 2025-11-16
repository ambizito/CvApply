"""Screen package aggregating all Tkinter screens."""
from .auto_login import AutoLoginScreen
from .credentials import CredentialsScreen
from .home import HomeScreen
from .search_preferences import SearchPreferencesScreen
from .preflight import PreflightScreen

__all__ = [
    "AutoLoginScreen",
    "CredentialsScreen",
    "HomeScreen",
    "SearchPreferencesScreen",
    "PreflightScreen",
]
