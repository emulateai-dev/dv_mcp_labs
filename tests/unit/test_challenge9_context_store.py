"""Unit tests for the Challenge 9 context_store module and server_sse authz fix.

Verifies that:
  * the reported live secrets no longer appear in the seeded shared context
    (CWE-798 / CWE-312 remediation),
  * safe placeholder defaults are used when no env var is set,
  * environment variables override the defaults,
  * the seeded context preserves its shape (admin + system notes),
  * the search tool refuses non-admin callers and when no admin token is
    configured on the server (the broken access control the finding reported).
"""

from __future__ import annotations

import importlib
import os

import pytest

from challenges.hard.challenge9 import context_store as cs

# The live secret values reported by the finding (server_sse.py:23 and :28).
# None of these may appear in the seeded context after remediation.
REPORTED_LIVE_SECRETS = [
    "ProdDB_2025_!@#$",  # production database password
    "dv_mcp_api_9f8d7c6b5a41234567890abcdef",  # API key
]


@pytest.mark.unit
def test_build_initial_shared_context_uses_safe_defaults_when_unset():
    """When no env vars are set, non-functional placeholder values are used."""
    ctx = cs.build_initial_shared_context()
    assert set(ctx.keys()) == {"admin", "system"}
    assert "demo-db-password-not-a-real-secret" in ctx["admin"][0]["note"]
    assert "demo-api-key-not-a-real-secret" in ctx["system"][1]["note"]


@pytest.mark.unit
def test_reported_live_secrets_absent_from_defaults():
    """None of the reported live secrets may appear in the seeded context."""
    ctx = cs.build_initial_shared_context()
    blob = "\n".join(n["note"] for notes in ctx.values() for n in notes)
    for secret in REPORTED_LIVE_SECRETS:
        assert secret not in blob, f"reported live secret leaked: {secret!r}"


@pytest.mark.unit
def test_safe_defaults_themselves_are_not_the_live_secrets():
    """The default constants must not equal the reported live secrets."""
    for name, default in cs._SAFE_DEFAULTS.items():
        for secret in REPORTED_LIVE_SECRETS:
            assert default != secret


@pytest.mark.unit
def test_env_var_overrides_default_for_each_secret():
    """Each DVMCP_CHALLENGE9_* env var must override its placeholder default."""
    overrides = {
        "DVMCP_CHALLENGE9_DB_PASSWORD": "injected-db-password",
        "DVMCP_CHALLENGE9_API_KEY": "injected-api-key",
    }
    for var, val in overrides.items():
        os.environ[var] = val

    importlib.reload(cs)
    ctx = cs.build_initial_shared_context()
    for val in overrides.values():
        assert val in "\n".join(n["note"] for notes in ctx.values() for n in notes)
    for default in cs._SAFE_DEFAULTS.values():
        assert default not in "\n".join(n["note"] for notes in ctx.values() for n in notes)


@pytest.mark.unit
def test_seeded_context_preserves_shape():
    """The admin/system note shape is preserved so the challenge stays usable."""
    ctx = cs.build_initial_shared_context()
    assert len(ctx["admin"]) == 2
    assert len(ctx["system"]) == 2
    for notes in ctx.values():
        for n in notes:
            assert "timestamp" in n and "note" in n


@pytest.mark.unit
def test_search_global_notes_denies_caller_when_no_admin_token_configured(monkeypatch):
    """No admin token configured on the server -> search is refused for all."""
    import challenges.hard.challenge9.server_sse as srv
    monkeypatch.setattr(srv, "ADMIN_TOKEN", None)
    srv.SHARED_CONTEXT = cs.build_initial_shared_context()

    # Instantiate the server so the @self.mcp.tool() closures are registered and
    # become reachable on the instance (they close over SHARED_CONTEXT/ADMIN_TOKEN).
    server = srv.Challenge9Server()
    # Find the search tool closure registered on the FastMCP instance.
    tools = server.mcp._tool_manager._tools
    search = next(t for t in tools.values() if t.name == "search_global_notes")
    result = search.fn(query="password", admin_token="anything")
    assert result.startswith("Access denied")


@pytest.mark.unit
def test_search_global_notes_denies_wrong_token(monkeypatch):
    """Wrong admin token -> search is refused."""
    import challenges.hard.challenge9.server_sse as srv
    monkeypatch.setattr(srv, "ADMIN_TOKEN", "real-admin-token")
    srv.SHARED_CONTEXT = cs.build_initial_shared_context()

    server = srv.Challenge9Server()
    tools = server.mcp._tool_manager._tools
    search = next(t for t in tools.values() if t.name == "search_global_notes")
    result = search.fn(query="password", admin_token="wrong-token")
    assert result.startswith("Access denied")


@pytest.mark.unit
def test_search_global_notes_allows_correct_token(monkeypatch):
    """Correct admin token -> search returns results (admin still works)."""
    import challenges.hard.challenge9.server_sse as srv
    monkeypatch.setattr(srv, "ADMIN_TOKEN", "real-admin-token")
    ctx = cs.build_initial_shared_context()
    # Inject a known queryable note so we can assert a hit.
    ctx["admin"][0]["note"] = "Reminder: the password is hunter2"
    srv.SHARED_CONTEXT = ctx

    server = srv.Challenge9Server()
    tools = server.mcp._tool_manager._tools
    search = next(t for t in tools.values() if t.name == "search_global_notes")
    result = search.fn(query="password", admin_token="real-admin-token")
    assert result.startswith("--- Search Results ---")
    assert "hunter2" in result
