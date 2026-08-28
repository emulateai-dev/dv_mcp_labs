"""Unit tests for Challenge 10 runtime system-config provisioning (CWE-798 / CWE-312)."""

import os

import pytest

from challenges.hard.challenge10.system_config import (
    get_system_config,
    _get_runtime_credential,
    SAFE_DEFAULT_CREDENTIALS,
    ENV_VAR_MAP,
)


@pytest.mark.unit
def test_get_runtime_credential_uses_placeholder_when_env_unset(monkeypatch):
    for var in ENV_VAR_MAP.values():
        monkeypatch.delenv(var, raising=False)
    assert _get_runtime_credential("api_gateway_secret") == SAFE_DEFAULT_CREDENTIALS["api_gateway_secret"]
    assert _get_runtime_credential("db_password") == SAFE_DEFAULT_CREDENTIALS["db_password"]


@pytest.mark.unit
def test_get_runtime_credential_prefers_env_override(monkeypatch):
    monkeypatch.setenv(ENV_VAR_MAP["api_gateway_secret"], "real-gateway-secret")
    assert _get_runtime_credential("api_gateway_secret") == "real-gateway-secret"


@pytest.mark.unit
def test_get_system_config_contains_labels_without_real_secrets(monkeypatch):
    for var in ENV_VAR_MAP.values():
        monkeypatch.delenv(var, raising=False)
    conf = get_system_config()
    # The structural labels the challenge depends on are still present
    assert "API Gateway" in conf
    assert "Secret:" in conf
    assert "AWS Access Key ID" in conf
    # None of the previously-hardcoded real-looking secrets appear
    assert "9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g" not in conf
    assert "Pr0d-DB-S3cur3!P@$$w0rd" not in conf
    assert "apg-prod-8a7b6c5d4e3f2g1h" not in conf
    assert "AKIAIOSFODNN7EXAMPLE" not in conf
    assert "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" not in conf


@pytest.mark.unit
def test_get_system_config_uses_env_override(monkeypatch):
    monkeypatch.setenv(ENV_VAR_MAP["api_gateway_secret"], "injected-gateway-secret")
    conf = get_system_config()
    assert "injected-gateway-secret" in conf
    assert SAFE_DEFAULT_CREDENTIALS["api_gateway_secret"] not in conf


@pytest.mark.unit
def test_no_real_secret_in_system_config_source():
    src = os.path.join(
        os.path.dirname(__file__), "..", "..", "challenges", "hard", "challenge10", "system_config.py"
    )
    text = open(src).read()
    assert "9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g" not in text
    assert "Pr0d-DB-S3cur3!P@$$w0rd" not in text
    assert "apg-prod-8a7b6c5d4e3f2g1h" not in text
    assert "AKIAIOSFODNN7EXAMPLE" not in text
    assert "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" not in text


@pytest.mark.unit
def test_no_real_secret_in_server_sse_source():
    src = os.path.join(
        os.path.dirname(__file__), "..", "..", "challenges", "hard", "challenge10", "server_sse.py"
    )
    text = open(src).read()
    assert "9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g" not in text
    assert "Pr0d-DB-S3cur3!P@$$w0rd" not in text
    assert "apg-prod-8a7b6c5d4e3f2g1h" not in text
    assert "AKIAIOSFODNN7EXAMPLE" not in text
    assert "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY" not in text
