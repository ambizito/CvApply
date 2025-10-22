from __future__ import annotations

import logging
import time
from dataclasses import dataclass
from typing import Iterable, List, Optional

import requests
from requests import Response
from requests.exceptions import RequestException

from .session_manager import Credentials, SessionManager


LOGGER = logging.getLogger(__name__)


@dataclass(slots=True)
class SystemCheckResult:
    """Structured outcome for a single health check."""

    name: str
    success: bool
    details: str = ""
    error: Optional[Exception] = None


class SystemCheck:
    """Base class for concrete system checks."""

    name: str
    description: str

    def __init__(self, name: str, description: str) -> None:
        self.name = name
        self.description = description

    def run(self) -> SystemCheckResult:  # pragma: no cover - override required
        raise NotImplementedError


class InternetConnectivityCheck(SystemCheck):
    """Ensure basic HTTP connectivity by requesting the Google homepage."""

    def __init__(self, timeout: float = 10.0) -> None:
        super().__init__(
            name="Conexão com a internet",
            description="Realiza uma requisição simples para o Google e valida o conteúdo retornado.",
        )
        self.timeout = timeout

    def run(self) -> SystemCheckResult:
        try:
            response = requests.get("https://www.google.com", timeout=self.timeout)
            response.raise_for_status()
        except RequestException as exc:  # pragma: no cover - network errors
            return SystemCheckResult(self.name, False, "Falha de conexão com a internet.", exc)

        if "Google" not in response.text:
            return SystemCheckResult(
                self.name,
                False,
                "Resposta inesperada de https://www.google.com.",
            )

        return SystemCheckResult(self.name, True, "Conexão estabelecida com sucesso.")


class LinkedInAccessCheck(SystemCheck):
    """Try to reach LinkedIn's homepage with retries and interval."""

    def __init__(self, retries: int = 5, delay_seconds: float = 5.0, timeout: float = 10.0) -> None:
        super().__init__(
            name="Acesso ao LinkedIn",
            description="Valida o acesso à página inicial do LinkedIn com tentativas adicionais em caso de erro.",
        )
        self.retries = retries
        self.delay_seconds = delay_seconds
        self.timeout = timeout

    def run(self) -> SystemCheckResult:
        last_error: Optional[Exception] = None
        for attempt in range(1, self.retries + 1):
            try:
                response: Response = requests.get("https://www.linkedin.com", timeout=self.timeout)
                response.raise_for_status()
            except RequestException as exc:
                last_error = exc
                LOGGER.error("Tentativa %s de acessar o LinkedIn falhou: %s", attempt, exc)
                if attempt < self.retries:
                    time.sleep(self.delay_seconds)
                continue

            if "LinkedIn" in response.text:
                return SystemCheckResult(self.name, True, "Página inicial do LinkedIn acessada.")

            last_error = ValueError("Conteúdo inesperado na página inicial do LinkedIn.")
            LOGGER.error("Tentativa %s falhou: %s", attempt, last_error)
            if attempt < self.retries:
                time.sleep(self.delay_seconds)

        return SystemCheckResult(
            self.name,
            False,
            "Não foi possível acessar a página inicial do LinkedIn após múltiplas tentativas.",
            last_error,
        )


class CredentialsExistCheck(SystemCheck):
    """Ensure the credential store contains LinkedIn username and password."""

    def __init__(self, session_manager: SessionManager) -> None:
        super().__init__(
            name="Credenciais disponíveis",
            description="Confere se email e senha do LinkedIn foram cadastrados.",
        )
        self._session_manager = session_manager

    def run(self) -> SystemCheckResult:
        credentials = self._session_manager.get_credentials()
        if credentials is None:
            return SystemCheckResult(self.name, False, "Nenhuma credencial cadastrada.")
        return SystemCheckResult(self.name, True, f"Credenciais encontradas para {credentials.email}.")


class CredentialsValidator:
    """Simple validation helper for stored credentials."""

    MIN_PASSWORD_LENGTH = 8

    @classmethod
    def is_valid(cls, credentials: Credentials) -> tuple[bool, str]:
        email = credentials.email.strip()
        password = credentials.password
        if "@" not in email or email.startswith("@") or email.endswith("@"):  # pragma: no cover - defensive
            return False, "Email inválido."
        if len(password) < cls.MIN_PASSWORD_LENGTH:
            return False, "A senha cadastrada é muito curta."
        return True, "Credenciais com formato válido."


class CredentialsValidityCheck(SystemCheck):
    """Validate the format of stored credentials."""

    def __init__(self, session_manager: SessionManager) -> None:
        super().__init__(
            name="Formato das credenciais",
            description="Verifica se email e senha atendem aos requisitos mínimos.",
        )
        self._session_manager = session_manager

    def run(self) -> SystemCheckResult:
        credentials = self._session_manager.get_credentials()
        if credentials is None:
            return SystemCheckResult(self.name, False, "Credenciais indisponíveis para validação.")
        valid, message = CredentialsValidator.is_valid(credentials)
        return SystemCheckResult(self.name, valid, message)


class SystemTestRunner:
    """Aggregate and execute predefined system checks."""

    def __init__(self, session_manager: SessionManager) -> None:
        self._session_manager = session_manager

    def get_checks(self) -> List[SystemCheck]:
        return [
            InternetConnectivityCheck(),
            LinkedInAccessCheck(),
            CredentialsExistCheck(self._session_manager),
            CredentialsValidityCheck(self._session_manager),
        ]

    def run_checks(self) -> Iterable[SystemCheckResult]:
        for check in self.get_checks():
            yield check.run()

