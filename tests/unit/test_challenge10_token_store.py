"""Unit tests for Challenge 10 runtime token provisioning (CWE-798 / CWE-312)."""

import json
import os
from pathlib import Path

import pytest

from challenges.hard.challenge10.token_store import (
    get_tokens,
    write_tokens,
    _DEFAULT_ADMIN_TOKEN,
    _DEFAULT_SERVICE_TOKEN,
    _DEFAULT_USER_TOKEN,
    _ENV_ADMIN_TOKEN,
    _ENV_SERVICE_TOKEN,
    _ENV_USER_TOKEN,
)


@pytest.mark.unit
def test_get_tokens_uses_placeholders_when_env_unset(monkeypatch):
    for var in (_ENV_ADMIN_TOKEN, _ENV_SERVICE_TOKEN, _ENV_USER_TOKEN):
        monkeypatch.delenv(var, raising=False)
    tokens = get_tokens()
    assert tokens["admin_token"] == _DEFAULT_ADMIN_TOKEN
    assert tokens["service_token"] == _DEFAULT_SERVICE_TOKEN
    assert tokens["user_token"] == _DEFAULT_USER_TOKEN


@pytest.mark.unit
def test_get_tokens_prefers_env_overrides(monkeypatch):
    monkeypatch.setenv(_ENV_ADMIN_TOKEN, "real-admin")
    monkeypatch.setenv(_ENV_SERVICE_TOKEN, "real-service")
    monkeypatch.setenv(_ENV_USER_TOKEN, "real-user")
    tokens = get_tokens()
    assert tokens == {
        "admin_token": "real-admin",
        "service_token": "real-service",
        "user_token": "real-user",
    }


@pytest.mark.unit
def test_get_tokens_trims_whitespace(monkeypatch):
    monkeypatch.setenv(_ENV_ADMIN_TOKEN, "  spaced-admin  ")
    tokens = get_tokens()
    assert tokens["admin_token"] == "spaced-admin"


@pytest.mark.unit
def test_write_tokens_materializes_json(tmp_path):
    target = tmp_path / "config" / "tokens.json"
    content = write_tokens(str(target))
    assert target.exists()
    on_disk = json.loads(target.read_text())
    assert on_disk == get_tokens()
    # Placeholders must never look like real JWTs (no "eyJ" header segment)
    for value in on_disk.values():
        assert not value.startswith("eyJ")


@pytest.mark.unit
def test_no_real_jwt_in_token_store_source():
    src = Path(__file__).resolve().parents[2] / "challenges/hard/challenge10/token_store.py"
    text = src.read_text()
    assert "eyJhbGci" not in text
    assert "8FhJ7Z5KFUEJFoQW2xeUL9_NOzlKB3j8fKvxU_5qB4Y" not in text


@pytest.mark.unit
def test_no_real_jwt_in_server_sse_source():
    src = Path(__file__).resolve().parents[2] / "challenges/hard/challenge10/server_sse.py"
    text = src.read_text()
    assert "eyJhbGci" not in text
    assert "8FhJ7Z5KFUEJFoQW2xeUL9_NOzlKB3j8fKvxU_5qB4Y" not in text
