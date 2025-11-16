"""Domain models encapsulating session management and system checks."""

from .scrap_user import ExperienceRecord, ScrapUserRepository
from .search_preferences import (
    ALLOWED_DATE_FILTERS,
    ALLOWED_EXPERIENCE_LEVELS,
    SearchPreferences,
    SearchPreferencesRepository,
)
from .session import Credentials, SessionManager, SessionStatus
from .system import (
    CredentialsExistCheck,
    CredentialsValidityCheck,
    InternetConnectivityCheck,
    LinkedInAccessCheck,
    SystemCheck,
    SystemCheckResult,
    SystemTestRunner,
)

__all__ = [
    "Credentials",
    "ExperienceRecord",
    "CredentialsExistCheck",
    "CredentialsValidityCheck",
    "InternetConnectivityCheck",
    "LinkedInAccessCheck",
    "ScrapUserRepository",
    "SearchPreferences",
    "SearchPreferencesRepository",
    "ALLOWED_DATE_FILTERS",
    "ALLOWED_EXPERIENCE_LEVELS",
    "SessionManager",
    "SessionStatus",
    "SystemCheck",
    "SystemCheckResult",
    "SystemTestRunner",
]
