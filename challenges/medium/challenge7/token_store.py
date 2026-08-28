"""Runtime token provisioning for Challenge 7 (Token Theft).

The challenge server materializes a ``tokens.json`` file on first boot.
Historically this file was seeded with hardcoded, real-looking API keys,
access tokens (JWTs) and refresh tokens checked directly into source control
(CWE-798 / CWE-312). Those secrets leaked into the repository and into every
container image built from it.

This module keeps operational tokens out of source control. Each value is
read from a deployment-supplied environment variable and falls back to a
clearly-marked, non-functional placeholder value only when no override is
configured — so the challenge still boots in a fresh checkout without
exposing any real secret.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# Default placeholder tokens. These are NOT real credentials: they are
# obviously-fake demo values that make it clear at a glance they are not
# live secrets. They must never be treated as valid in any production-style
# check.
_DEFAULTS = {
    "email_service": {
        "service_name": "EmailPro API",
        "api_key": "demo-email-api-key-not-a-real-secret",
        "access_token": "demo-email-access-token-not-a-real-secret",
        "refresh_token": "demo-email-refresh-token-not-a-real-secret",
        "expires_at": "2025-12-31T23:59:59Z",
    },
    "cloud_storage": {
        "service_name": "CloudBox Storage",
        "api_key": "demo-cloud-storage-api-key-not-a-real-secret",
        "access_token": "demo-cloud-storage-access-token-not-a-real-secret",
        "refresh_token": "demo-cloud-storage-refresh-token-not-a-real-secret",
        "expires_at": "2025-12-31T23:59:59Z",
    },
    "analytics_platform": {
        "service_name": "DataMetrics Analytics",
        "api_key": "demo-analytics-api-key-not-a-real-secret",
        "access_token": "demo-analytics-access-token-not-a-real-secret",
        "refresh_token": "demo-analytics-refresh-token-not-a-real-secret",
        "expires_at": "2025-12-31T23:59:59Z",
    },
}

# Environment variables a deployment can set to inject real tokens out-of-band.
# Keys: <service_id>; values: env var names for each secret field.
_ENV_VAR_MAP = {
    "email_service": {
        "api_key": "DVMCP_CHALLENGE7_EMAIL_API_KEY",
        "access_token": "DVMCP_CHALLENGE7_EMAIL_ACCESS_TOKEN",
        "refresh_token": "DVMCP_CHALLENGE7_EMAIL_REFRESH_TOKEN",
    },
    "cloud_storage": {
        "api_key": "DVMCP_CHALLENGE7_CLOUD_STORAGE_API_KEY",
        "access_token": "DVMCP_CHALLENGE7_CLOUD_STORAGE_ACCESS_TOKEN",
        "refresh_token": "DVMCP_CHALLENGE7_CLOUD_STORAGE_REFRESH_TOKEN",
    },
    "analytics_platform": {
        "api_key": "DVMCP_CHALLENGE7_ANALYTICS_API_KEY",
        "access_token": "DVMCP_CHALLENGE7_ANALYTICS_ACCESS_TOKEN",
        "refresh_token": "DVMCP_CHALLENGE7_ANALYTICS_REFRESH_TOKEN",
    },
}

# Static, non-secret fields that do not need per-deployment override.
_STATIC_FIELDS = ("service_name", "expires_at")

DEFAULT_TOKENS_PATH = "/tmp/dvmcp_challenge7/tokens.json"


def _resolve(env_var: str, default: str) -> str:
    """Return the configured token, or a safe placeholder default."""
    value = os.getenv(env_var, "").strip()
    return value or default


def get_tokens() -> dict:
    """Return the challenge token map, sourced from the environment.

    Real tokens are injected via ``DVMCP_CHALLENGE7_*`` environment variables
    by the deployment. When unset, non-functional placeholder values are used
    so the demo still boots without leaking secrets in source control.
    """
    tokens = {}
    for service_id, defaults in _DEFAULTS.items():
        service = {field: defaults[field] for field in _STATIC_FIELDS}
        for field, default_value in defaults.items():
            if field in _STATIC_FIELDS:
                continue
            env_var = _ENV_VAR_MAP[service_id][field]
            service[field] = _resolve(env_var, default_value)
        tokens[service_id] = service
    return tokens


def write_tokens(path: str = DEFAULT_TOKENS_PATH) -> str:
    """Materialize ``tokens.json`` at ``path`` and return the written JSON.

    The directory is created if needed. The on-disk content mirrors the
    previous shape of the file so existing challenge tooling keeps working.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    tokens = get_tokens()
    content = json.dumps(tokens, indent=2)
    target.write_text(content + "\n")
    return content


if __name__ == "__main__":  # pragma: no cover - CLI entry for boot scripts
    import sys
    if len(sys.argv) > 1 and sys.argv[1] != "write_tokens":
        sys.exit(f"Unknown command: {sys.argv[1]}")
    print(write_tokens())
