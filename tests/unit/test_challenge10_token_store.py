"""Unit tests for the Challenge 10 runtime token store.

Verifies that no hardcoded JWTs are emitted by ``token_store`` and that the
challenge server provisions ``tokens.json`` from environment configuration
instead of source-controlled secrets (CWE-798 / CWE-312).
"""
import json
import os
import sys
from pathlib import Path

import pytest

CHALLENGE_DIR = Path(__file__).resolve().parents[2] / "challenges" / "hard" / "challenge10"
sys.path.insert(0, str(CHALLENGE_DIR))

import token_store  # noqa: E402

_ENV_VARS = (
    "DVMCP_CHALLENGE10_ADMIN_TOKEN",
    "DVMCP_CHALLENGE10_SERVICE_TOKEN",
    "DVMCP_CHALLENGE10_USER_TOKEN",
)


@pytest.fixture(autouse=True)
def _clean_env():
    saved = {v: os.environ.pop(v, None) for v in _ENV_VARS}
    yield
    for v, val in saved.items():
        if val is not None:
            os.environ[v] = val
        else:
            os.environ.pop(v, None)


def test_get_tokens_returns_placeholders_when_unset():
    tokens = token_store.get_tokens()
    assert tokens == {
        "admin_token": "demo-admin-token-not-a-real-secret",
        "service_token": "demo-service-token-not-a-real-secret",
        "user_token": "demo-user-token-not-a-real-secret",
    }


def test_get_tokens_reads_env_overrides():
    os.environ["DVMCP_CHALLENGE10_ADMIN_TOKEN"] = "real-admin"
    os.environ["DVMCP_CHALLENGE10_SERVICE_TOKEN"] = "real-service"
    os.environ["DVMCP_CHALLENGE10_USER_TOKEN"] = " real-user-spaced "
    tokens = token_store.get_tokens()
    assert tokens == {
        "admin_token": "real-admin",
        "service_token": "real-service",
        "user_token": "real-user-spaced",
    }


def test_no_hardcoded_jwt_in_default_tokens():
    tokens = token_store.get_tokens()
    blob = json.dumps(tokens)
    assert "eyJ" not in blob, "hardcoded JWT leaked into default token set"


def test_write_tokens_materializes_file_without_jwt(tmp_path):
    path = tmp_path / "tokens.json"
    content = token_store.write_tokens(str(path))
    assert "eyJ" not in content
    on_disk = json.loads(path.read_text())
    assert on_disk["admin_token"] == "demo-admin-token-not-a-real-secret"


def test_server_sse_source_has_no_hardcoded_jwt():
    src = (CHALLENGE_DIR / "server_sse.py").read_text()
    assert "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9" not in src, (
        "hardcoded JWT still present in server_sse.py"
    )
    assert "get_tokens()[" in src
    assert "write_tokens(" in src
