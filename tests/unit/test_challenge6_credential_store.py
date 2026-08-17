"""Unit tests for the Challenge 6 credential_store module.

These confirm that:
  * the live secrets reported by the finding are NOT present in the defaults,
  * the defaults returned are clearly non-functional placeholders,
  * deployment overrides via DVMCP_CHALLENGE6_* env vars are honoured.
"""

import importlib

import pytest


@pytest.fixture
def credential_store():
    """Import the credential_store module fresh for each test."""
    import importlib.util
    import os

    spec = importlib.util.spec_from_file_location(
        "challenge6_credential_store",
        os.path.join("challenges", "medium", "challenge6", "credential_store.py"),
    )
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


# The live values reported by the finding - must never reappear in source.
LEAKED_SECRETS = [
    "api_prod_8a7b6c5d4e3f2g1h",
    "pg_live_9i8u7y6t5r4e3w2q",
    "as_prod_2p3o4i5u6y7t8r9e",
    "api_dev_1a2b3c4d5e6f7g8h",
    "pg_test_9i8u7y6t5r4e3w2q",
    "as_dev_2p3o4i5u6y7t8r9e",
]


def test_defaults_do_not_contain_leaked_secrets(credential_store):
    for name in credential_store.SAFE_DEFAULT_CREDENTIALS:
        value = credential_store._get_runtime_credential(name)
        for secret in LEAKED_SECRETS:
            assert secret not in value


def test_defaults_are_placeholder_values(credential_store, monkeypatch):
    # Ensure no env overrides are set.
    for env_var in credential_store.ENV_VAR_MAP.values():
        monkeypatch.delenv(env_var, raising=False)

    for name, default in credential_store.SAFE_DEFAULT_CREDENTIALS.items():
        assert credential_store._get_runtime_credential(name) == default
        # Placeholder defaults must not look like real keys.
        assert "not-a-real-secret" in default


def test_env_var_override_is_honoured(credential_store, monkeypatch):
    monkeypatch.setenv(
        credential_store.ENV_VAR_MAP["main_api_prod"],
        "runtime-main-api-key",
    )
    assert (
        credential_store._get_runtime_credential("main_api_prod")
        == "runtime-main-api-key"
    )


def test_get_internal_memo_uses_runtime_credentials(credential_store, monkeypatch):
    monkeypatch.setenv(
        credential_store.ENV_VAR_MAP["main_api_prod"],
        "runtime-main-api-key",
    )
    memo = credential_store.get_internal_memo()
    assert "runtime-main-api-key" in memo
    # None of the leaked live keys should appear in the memo body.
    for secret in LEAKED_SECRETS:
        assert secret not in memo


def test_get_api_keys_uses_runtime_credentials(credential_store, monkeypatch):
    monkeypatch.setenv(
        credential_store.ENV_VAR_MAP["payment_gateway_dev"],
        "runtime-dev-pg-key",
    )
    keys = credential_store.get_api_keys()
    assert "runtime-dev-pg-key" in keys
    for secret in LEAKED_SECRETS:
        assert secret not in keys
