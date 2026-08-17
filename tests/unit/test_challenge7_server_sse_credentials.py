"""Unit tests verifying the Challenge 7 SSE server no longer hardcodes
secrets in source (CWE-798 / CWE-312) and that the credential_store
env-var overrides work."""
import importlib
import os
import sys
from pathlib import Path

import pytest

CHALLENGE_DIR = Path(__file__).resolve().parents[2] / "challenges" / "medium" / "challenge7"


@pytest.fixture
def credential_store():
    sys.path.insert(0, str(CHALLENGE_DIR))
    import credential_store as cs
    importlib.reload(cs)
    yield cs
    sys.path.remove(str(CHALLENGE_DIR))


def test_admin_api_token_default_is_non_live(credential_store):
    token = credential_store.get_admin_api_token()
    assert token == credential_store.ADMIN_API_TOKEN_DEFAULT
    assert "not-a-real-secret" in token


def test_admin_api_token_env_override(monkeypatch, credential_store):
    monkeypatch.setenv("DVMCP_CHALLENGE7_ADMIN_API_TOKEN", "operator-supplied-admin-token")
    assert credential_store.get_admin_api_token() == "operator-supplied-admin-token"


def test_admin_system_secrets_default_is_non_live(credential_store):
    secrets = credential_store.get_admin_system_secrets()
    assert set(secrets) == {"DB_PASSWORD", "INTERNAL_API_KEY", "S3_BUCKET"}
    for value in secrets.values():
        assert "not-a-real" in value


def test_admin_system_secrets_env_override(monkeypatch, credential_store):
    monkeypatch.setenv("DVMCP_CHALLENGE7_ADMIN_DB_PASSWORD", "op-db-pw")
    monkeypatch.setenv("DVMCP_CHALLENGE7_ADMIN_INTERNAL_API_KEY", "op-internal-key")
    monkeypatch.setenv("DVMCP_CHALLENGE7_ADMIN_S3_BUCKET", "op-bucket")
    secrets = credential_store.get_admin_system_secrets()
    assert secrets == {
        "DB_PASSWORD": "op-db-pw",
        "INTERNAL_API_KEY": "op-internal-key",
        "S3_BUCKET": "op-bucket",
    }


def test_no_live_secret_remains_in_source():
    """The specific live-looking secrets reported by the finding must not
    appear anywhere in the challenge7 source tree."""
    live_secrets = [
        "mcp-admin-9f8e7d6c5b4a3210",
        "prod_db_s3cr3t_2025!",
        "int-api-4f5e6d7c8b9a",
        "company-financials-prod",
    ]
    offenders = []
    for py_file in CHALLENGE_DIR.glob("*.py"):
        text = py_file.read_text()
        for secret in live_secrets:
            if secret in text:
                offenders.append(f"{py_file.name}:{secret}")
    assert not offenders, f"live secrets still in source: {offenders}"
