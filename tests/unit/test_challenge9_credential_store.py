"""Unit tests for the Challenge 9 credential_store module.

Verifies that:
  * the reported live secrets no longer appear in the seeded context notes
    (CWE-798 / CWE-312 remediation),
  * safe placeholder defaults are used when no env var is set,
  * environment variables override the defaults,
  * build_shared_context preserves the expected dict shape so existing
    challenge tooling (reading cross-session context) keeps working.
"""

from __future__ import annotations

import importlib
import os

import pytest

from challenges.hard.challenge9 import credential_store as cs

# The live secret values reported by the finding (server_sse.py:64).
# None of these may appear in the generated output after remediation.
REPORTED_LIVE_SECRETS = [
    "ProdDB_2025_!@#$",  # production database password
    "dv_mcp_api_9f8d7c6b5a41234567890abcdef",  # system API key
]


@pytest.fixture
def challenge9_env(monkeypatch):
    """Clear the Challenge 9 env vars for a deterministic baseline."""
    for var in (
        "DVMCP_CHALLENGE9_ADMIN_DB_PASSWORD",
        "DVMCP_CHALLENGE9_SYSTEM_API_KEY",
    ):
        monkeypatch.delenv(var, raising=False)
    return monkeypatch


@pytest.mark.unit
def test_build_shared_context_uses_safe_defaults_when_unset(challenge9_env):
    """When no env vars are set, non-functional placeholder notes are used."""
    ctx = cs.build_shared_context(now=1_000_000)

    assert set(ctx.keys()) == {"admin", "system"}
    assert len(ctx["admin"]) == 2
    assert len(ctx["system"]) == 2

    # Timestamps are deterministic relative to `now`.
    assert ctx["admin"][0]["timestamp"] == 1_000_000 - 3600
    assert ctx["admin"][1]["timestamp"] == 1_000_000 - 1800
    assert ctx["system"][0]["timestamp"] == 1_000_000 - 86400
    assert ctx["system"][1]["timestamp"] == 1_000_000 - 86399

    # The non-secret operational note is preserved.
    assert "Meeting with security team" in ctx["admin"][1]["note"]
    assert "Server initialized successfully" in ctx["system"][0]["note"]

    # The secret-bearing notes point at the env-var mechanism rather than
    # embedding a real credential.
    assert "DVMCP_CHALLENGE9_ADMIN_DB_PASSWORD" in ctx["admin"][0]["note"]
    assert "DVMCP_CHALLENGE9_SYSTEM_API_KEY" in ctx["system"][1]["note"]


@pytest.mark.unit
def test_reported_live_secrets_absent_from_defaults(challenge9_env):
    """None of the reported live secrets may appear in the generated context."""
    ctx = cs.build_shared_context(now=1_000_000)
    for user_notes in ctx.values():
        for entry in user_notes:
            for secret in REPORTED_LIVE_SECRETS:
                assert secret not in entry["note"], (
                    f"reported live secret leaked: {secret!r}"
                )


@pytest.mark.unit
def test_safe_defaults_themselves_are_not_the_live_secrets():
    """The default constants must not equal the reported live secrets."""
    for default in cs._SAFE_DEFAULTS.values():
        for secret in REPORTED_LIVE_SECRETS:
            assert secret not in default


@pytest.mark.unit
def test_env_var_overrides_default_for_each_secret(monkeypatch):
    """Each DVMCP_CHALLENGE9_* env var must override its placeholder default."""
    monkeypatch.setenv("DVMCP_CHALLENGE9_ADMIN_DB_PASSWORD", "injected-db-password")
    monkeypatch.setenv("DVMCP_CHALLENGE9_SYSTEM_API_KEY", "injected-api-key")

    ctx = cs.build_shared_context(now=1_000_000)
    assert "injected-db-password" in ctx["admin"][0]["note"]
    assert "injected-api-key" in ctx["system"][1]["note"]
    # No placeholder-default env-var hint should remain once overridden.
    assert "DVMCP_CHALLENGE9_ADMIN_DB_PASSWORD" not in ctx["admin"][0]["note"]
    assert "DVMCP_CHALLENGE9_SYSTEM_API_KEY" not in ctx["system"][1]["note"]


@pytest.mark.unit
def test_explicit_value_overrides_env_var(monkeypatch):
    """An explicit value passed to build_shared_context wins over env vars."""
    monkeypatch.setenv("DVMCP_CHALLENGE9_ADMIN_DB_PASSWORD", "env-supplied-db-password")
    monkeypatch.setenv("DVMCP_CHALLENGE9_SYSTEM_API_KEY", "env-supplied-api-key")

    ctx = cs.build_shared_context(
        now=1_000_000,
        admin_db_password="explicit-db-password",
        system_api_key="explicit-api-key",
    )
    assert "explicit-db-password" in ctx["admin"][0]["note"]
    assert "explicit-api-key" in ctx["system"][1]["note"]
    assert "env-supplied-db-password" not in ctx["admin"][0]["note"]
    assert "env-supplied-api-key" not in ctx["system"][1]["note"]
