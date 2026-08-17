"""Unit tests for the Challenge 3 credential_store module.

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

from challenges.easy.challenge3 import credential_store as cs

# The live secret values reported by the finding (startup.sh:36-46 and the
# hardcoded system_credentials block in challenges/easy/challenge3/server.py).
# None of these may appear in the generated output after remediation.
REPORTED_LIVE_SECRETS = [
    "Pr0d-DB-S3cret!",  # database password
    "ACME-CLOUD-92731",  # cloud account id
    "ak_live_7y2JHGd8sKlM9nPzXqRt5vWx",  # cloud API key
    "cs_live_bNp5T2vR8sKlM9nQzXwJhGf4",  # cloud API secret
]


@pytest.mark.unit
def test_get_credentials_uses_safe_defaults_when_unset():
    """When no env vars are set, non-functional placeholder values are used."""
    content = cs.get_credentials()
    assert "SYSTEM CREDENTIALS - HIGHLY RESTRICTED" in content
    assert "demo-db-password-not-a-real-secret" in content
    assert "ACME-DEMO-CLOUD-NOT-REAL" in content
    assert "ak_demo_NotARealApiKey0123456789" in content
    assert "cs_demo_NotARealSecret0123456789abcdef" in content
    # Non-secret operational config is preserved so the challenge stays usable.
    assert "db.acmecorp.internal" in content
    assert "admin_prod" in content


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
    """Each DVMCP_CHALLENGE3_* env var must override its placeholder default."""
    overrides = {
        "DVMCP_CHALLENGE3_DB_PASSWORD": "injected-db-password",
        "DVMCP_CHALLENGE3_CLOUD_ACCOUNT_ID": "ACME-INJECTED-CLOUD",
        "DVMCP_CHALLENGE3_CLOUD_API_KEY": "ak_injected_NotARealKey",
        "DVMCP_CHALLENGE3_CLOUD_API_SECRET": "cs_injected_NotARealSecret",
    }
    for var, val in overrides.items():
        os.environ[var] = val

    # Reload so module-level state picks up env.
    importlib.reload(cs)

    content = cs.get_credentials()
    for val in overrides.values():
        assert val in content
    # No placeholder defaults should remain once everything is overridden.
    for default in cs._SAFE_DEFAULTS.values():
        assert default not in content


@pytest.mark.unit
def test_write_credentials_creates_file_with_expected_content(tmp_path):
    """write_credentials materializes system_credentials.txt with the right shape."""
    target = tmp_path / "private" / "system_credentials.txt"
    written = cs.write_credentials(str(target))

    assert target.exists()
    on_disk = target.read_text()
    assert on_disk == written
    assert "SYSTEM CREDENTIALS - HIGHLY RESTRICTED" in on_disk
    assert "Production Database:" in on_disk
    assert "Cloud Infrastructure:" in on_disk


@pytest.mark.unit
def test_get_credentials_has_trailing_newline_for_file_shape():
    """Output must end with a newline to match the original file shape."""
    assert cs.get_credentials().endswith("\n")
