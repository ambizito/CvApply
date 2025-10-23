from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from requests.exceptions import RequestException

from src.app.models.session import SessionManager
from src.app.models.system import (
    CredentialsExistCheck,
    CredentialsValidityCheck,
    InternetConnectivityCheck,
    LinkedInAccessCheck,
)


class DummyResponse(SimpleNamespace):
    def raise_for_status(self) -> None:  # pragma: no cover - mocks mimic requests.Response
        if getattr(self, "status_code", 200) >= 400:
            raise AssertionError("HTTP error")


@pytest.fixture()
def session_manager(tmp_path):
    return SessionManager(tmp_path)


def test_internet_connectivity_check_success(monkeypatch):
    check = InternetConnectivityCheck()

    mock_response = DummyResponse(status_code=200, text="<html>Google</html>")
    monkeypatch.setattr("src.app.models.system.requests.get", lambda *args, **kwargs: mock_response)

    result = check.run()
    assert result.success
    assert "Conexão estabelecida" in result.details


def test_linkedin_access_check_retries_until_success(monkeypatch):
    check = LinkedInAccessCheck(retries=3, delay_seconds=0)

    responses = [
        Mock(side_effect=RequestException("Erro temporário")),
        Mock(return_value=DummyResponse(status_code=200, text="LinkedIn")),
    ]

    def fake_get(*args, **kwargs):
        call = responses.pop(0)
        return call()

    monkeypatch.setattr("src.app.models.system.requests.get", fake_get)
    monkeypatch.setattr("src.app.models.system.time.sleep", lambda *args, **kwargs: None)

    result = check.run()
    assert result.success
    assert "LinkedIn" in result.details


def test_linkedin_access_check_failure(monkeypatch):
    check = LinkedInAccessCheck(retries=2, delay_seconds=0)

    monkeypatch.setattr(
        "src.app.models.system.requests.get",
        Mock(side_effect=RequestException("Falha permanente")),
    )
    monkeypatch.setattr("src.app.models.system.time.sleep", lambda *args, **kwargs: None)

    result = check.run()
    assert not result.success
    assert "Não foi possível" in result.details


def test_credentials_checks(session_manager):
    exist_check = CredentialsExistCheck(session_manager)
    validity_check = CredentialsValidityCheck(session_manager)

    missing = exist_check.run()
    assert not missing.success

    session_manager.save_credentials("user@example.com", "password123")

    exist = exist_check.run()
    assert exist.success

    valid = validity_check.run()
    assert valid.success


def test_invalid_credentials_are_reported(session_manager):
    validity_check = CredentialsValidityCheck(session_manager)
    session_manager.save_credentials("user@example.com", "short")

    result = validity_check.run()
    assert not result.success
    assert "curta" in result.details
