"""Screen package aggregating all Tkinter screens."""
from .auto_login import AutoLoginScreen
from .credentials import CredentialsScreen
from .home import HomeScreen
from .onboarding import OnboardingScreen
from .preflight import PreflightScreen

__all__ = [
    "AutoLoginScreen",
    "CredentialsScreen",
    "HomeScreen",
    "OnboardingScreen",
    "PreflightScreen",
]
