"""Unit tests for the Challenge 8 credential_store module.

Verifies that:
  * the reported live secrets no longer appear in the generated credentials
    content (CWE-798 / CWE-312 remediation),
  * safe placeholder defaults are used when no env var is set,
  * environment variables override the defaults,
  * write_credentials materializes a file with the expected shape.
"""

from __future__ import annotations

import os
import importlib

import pytest

from challenges.hard.challenge8 import credential_store as cs

# The live secret values reported by the finding (startup.sh:67 and the rest of
# the hardcoded Challenge 8 credentials block). None of these may appear in the
# generated output after remediation.
REPORTED_LIVE_SECRETS = [
    "Pr0d-DB-S3cur3!P@$$w0rd",  # database password
    "AKIAIOSFODNN7EXAMPLE",  # AWS access key id
    "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",  # AWS secret access key
    "apg-prod-8a7b6c5d4e3f2g1h",  # API Gateway key
    "9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g",  # API Gateway secret
]


@pytest.mark.unit
def test_get_credentials_uses_safe_defaults_when_unset():
    """When no env vars are set, non-functional placeholder values are used."""
    content = cs.get_credentials()
    assert "PRODUCTION CREDENTIALS" in content
    assert "demo-db-password-not-a-real-secret" in content
    assert "AKIADemoAccessKeyNotReal" in content
    assert "demo-aws-secret-access-key-not-a-real-secret" in content
    assert "demo-api-gateway-key-not-a-real-secret" in content
    assert "demo-api-gateway-secret-not-a-real-secret" in content
    # Non-secret operational config is preserved so the challenge stays usable.
    assert "db.acmecorp.internal" in content
    assert "db_admin" in content
    assert "us-west-2" in content


@pytest.mark.unit
def test_reported_live_secrets_absent_from_defaults():
    """None of the reported live secrets may appear in the generated content."""
    content = cs.get_credentials()
    for secret in REPORTED_LIVE_SECRETS:
        assert secret not in content, f"reported live secret leaked: {secret!r}"


@pytest.mark.unit
def test_safe_defaults_themselves_are_not_the_live_secrets():
    """The default constants must not equal the reported live secrets."""
    for name, default in cs._SAFE_DEFAULTS.items():
        for secret in REPORTED_LIVE_SECRETS:
            assert default != secret


@pytest.mark.unit
def test_env_var_overrides_default_for_each_secret():
    """Each DVMCP_CHALLENGE8_* env var must override its placeholder default."""
    overrides = {
        "DVMCP_CHALLENGE8_DB_PASSWORD": "injected-db-password",
        "DVMCP_CHALLENGE8_AWS_ACCESS_KEY_ID": "AKIAInjectedAccessKey",
        "DVMCP_CHALLENGE8_AWS_SECRET_ACCESS_KEY": "injected-aws-secret",
        "DVMCP_CHALLENGE8_API_GATEWAY_KEY": "injected-gateway-key",
        "DVMCP_CHALLENGE8_API_GATEWAY_SECRET": "injected-gateway-secret",
    }
    for var, val in overrides.items():
        os.environ[var] = val

    # Reload so module-level state (none dynamic here, but defensive) picks up env.
    importlib.reload(cs)

    content = cs.get_credentials()
    for val in overrides.values():
        assert val in content
    # No placeholder defaults should remain once everything is overridden.
    for default in cs._SAFE_DEFAULTS.values():
        assert default not in content


@pytest.mark.unit
def test_write_credentials_creates_file_with_expected_content(tmp_path):
    """write_credentials materializes credentials.txt with the right shape."""
    target = tmp_path / "sensitive" / "credentials.txt"
    written = cs.write_credentials(str(target))

    assert target.exists()
    on_disk = target.read_text()
    assert on_disk == written
    assert "PRODUCTION CREDENTIALS" in on_disk
    assert "Database:" in on_disk
    assert "AWS:" in on_disk
    assert "API Gateway:" in on_disk


@pytest.mark.unit
def test_get_credentials_has_trailing_newline_for_file_shape():
    """Output must end with a newline to match the original file shape."""
    assert cs.get_credentials().endswith("\n")
