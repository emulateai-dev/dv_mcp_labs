import json
import os
import sys
from pathlib import Path

import pytest

# Ensure the challenges package is importable when tests run from repo root.
ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from challenges.hard.challenge10 import token_store


class TestChallenge10TokenStore:
    """Unit tests for runtime token provisioning (CWE-798/CWE-312 remediation)."""

    @pytest.mark.unit
    def test_no_hardcoded_jwt_in_source(self):
        """The token_store module must not embed any real JWT string."""
        src = Path(token_store.__file__).read_text()
        assert "eyJhbGci" not in src, "real JWT material must not be in source"
        assert "8FhJ7Z5KFUEJFoQW2xeUL9" not in src

    @pytest.mark.unit
    def test_defaults_are_non_secret_placeholders(self, monkeypatch):
        """Without env vars, placeholders are clearly non-functional values."""
        for var in (
            "DVMCP_CHALLENGE10_ADMIN_TOKEN",
            "DVMCP_CHALLENGE10_SERVICE_TOKEN",
            "DVMCP_CHALLENGE10_USER_TOKEN",
        ):
            monkeypatch.delenv(var, raising=False)

        tokens = token_store.get_tokens()
        assert tokens["admin_token"] == "demo-admin-token-not-a-real-secret"
        assert tokens["service_token"] == "demo-service-token-not-a-real-secret"
        assert tokens["user_token"] == "demo-user-token-not-a-real-secret"
        # None of the defaults look like a real JWT.
        for value in tokens.values():
            assert not value.startswith("eyJ")

    @pytest.mark.unit
    def test_env_overrides_propagate(self, monkeypatch):
        """Deployment-supplied env vars are used verbatim."""
        monkeypatch.setenv("DVMCP_CHALLENGE10_ADMIN_TOKEN", "injected-admin-secret")
        monkeypatch.setenv("DVMCP_CHALLENGE10_SERVICE_TOKEN", "injected-service-secret")
        # leave USER unset -> default
        monkeypatch.delenv("DVMCP_CHALLENGE10_USER_TOKEN", raising=False)

        tokens = token_store.get_tokens()
        assert tokens["admin_token"] == "injected-admin-secret"
        assert tokens["service_token"] == "injected-service-secret"
        assert tokens["user_token"] == "demo-user-token-not-a-real-secret"

    @pytest.mark.unit
    def test_write_tokens_creates_valid_json(self, tmp_path, monkeypatch):
        """write_tokens materializes a JSON file matching the expected schema."""
        monkeypatch.setenv("DVMCP_CHALLENGE10_ADMIN_TOKEN", "env-admin")
        monkeypatch.delenv("DVMCP_CHALLENGE10_SERVICE_TOKEN", raising=False)
        monkeypatch.delenv("DVMCP_CHALLENGE10_USER_TOKEN", raising=False)

        target = tmp_path / "tokens.json"
        content = token_store.write_tokens(str(target))

        loaded = json.loads(target.read_text())
        assert loaded["admin_token"] == "env-admin"
        assert loaded["service_token"] == "demo-service-token-not-a-real-secret"
        assert loaded["user_token"] == "demo-user-token-not-a-real-secret"
        # returned content equals file content
        assert json.loads(content) == loaded

    @pytest.mark.unit
    def test_write_tokens_creates_parent_dir(self, tmp_path):
        """write_tokens should create a missing parent directory."""
        target = tmp_path / "nested" / "missing" / "tokens.json"
        token_store.write_tokens(str(target))
        assert target.exists()
