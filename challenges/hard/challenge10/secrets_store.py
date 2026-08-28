"""Runtime secret provisioning for Challenge 10 (``server.py``).

The standalone Challenge 10 MCP server (``challenges/hard/challenge10/server.py``)
materializes several on-disk artifacts for the demo:

* ``config/system.conf``  — a database password, an API-gateway key + secret and
  AWS access key id + secret access key,
* ``config/tokens.json``   — admin / service / user JWT tokens,
* ``data/users.json``      — user password *hashes* (sha256),
* and an in-memory admin-dashboard string carrying a "master password".

Historically all of those values were hardcoded directly in ``server.py`` and
committed to source control (CWE-798 / CWE-312). That leaked real-looking
production credentials, JWTs and cleartext "password: <value>" hints into the
repository and into every container image built from it.

This module keeps every one of those secrets out of source control. Real
values are read from deployment-supplied ``DVMCP_CHALLENGE10_*`` environment
variables; when unset, clearly-marked, non-functional placeholder values are
used so the challenge still boots from a fresh checkout without leaking any
real secret.

The hash defaults here are sha256 of the placeholder plaintexts — they are
NOT the hashes of any real credential and carry no recoverable secret.
"""

from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path

# ---------------------------------------------------------------------------
# Safe, non-functional placeholder defaults.
#
# None of these is a real credential. The token/hash strings are deterministic
# but obviously synthetic ("...-not-a-real-secret") and the password hashes are
# sha256 of those same placeholder plaintexts, so they carry no recoverable
# secret. They exist only so the challenge remains runnable without shipping
# secrets in source control.
# ---------------------------------------------------------------------------
SAFE_DEFAULTS = {
    "db_password": "demo-db-password-not-a-real-secret",
    "api_gateway_key": "demo-api-gateway-key-not-a-real-secret",
    "api_gateway_secret": "demo-api-gateway-secret-not-a-real-secret",
    "aws_access_key_id": "demo-aws-access-key-id-not-a-real-secret",
    "aws_secret_access_key": "demo-aws-secret-access-key-not-a-real-secret",
    "admin_token": "demo-admin-token-not-a-real-secret",
    "service_token": "demo-service-token-not-a-real-secret",
    "user_token": "demo-user-token-not-a-real-secret",
    "master_password": "demo-master-password-not-a-real-secret",
    # Demo user passwords (plaintext placeholders hashed with sha256).
    "admin_password": "demo-admin-password",
    "service_password": "demo-service-password",
    "user_password": "demo-user-password",
}

# Environment variables a deployment sets to inject real secrets out-of-band.
# Secrets must never live in source control (CWE-798 / CWE-312).
ENV_VAR_MAP = {
    "db_password": "DVMCP_CHALLENGE10_DB_PASSWORD",
    "api_gateway_key": "DVMCP_CHALLENGE10_API_GATEWAY_KEY",
    "api_gateway_secret": "DVMCP_CHALLENGE10_API_GATEWAY_SECRET",
    "aws_access_key_id": "DVMCP_CHALLENGE10_AWS_ACCESS_KEY_ID",
    "aws_secret_access_key": "DVMCP_CHALLENGE10_AWS_SECRET_ACCESS_KEY",
    "admin_token": "DVMCP_CHALLENGE10_ADMIN_TOKEN",
    "service_token": "DVMCP_CHALLENGE10_SERVICE_TOKEN",
    "user_token": "DVMCP_CHALLENGE10_USER_TOKEN",
    "master_password": "DVMCP_CHALLENGE10_MASTER_PASSWORD",
    "admin_password": "DVMCP_CHALLENGE10_ADMIN_PASSWORD",
    "service_password": "DVMCP_CHALLENGE10_SERVICE_PASSWORD",
    "user_password": "DVMCP_CHALLENGE10_USER_PASSWORD",
}

DEFAULT_TOKENS_PATH = "/tmp/dvmcp_challenge10/config/tokens.json"
DEFAULT_USERS_PATH = "/tmp/dvmcp_challenge10/data/users.json"


def _resolve(name: str) -> str:
    """Return the runtime value for ``name``, or its safe placeholder default.

    Real values are read from the matching ``DVMCP_CHALLENGE10_*`` environment
    variable; when unset, a clearly-marked non-functional placeholder is used.
    """
    value = os.getenv(ENV_VAR_MAP[name])
    return value if value else SAFE_DEFAULTS[name]


def _sha256(text: str) -> str:
    """Return the sha256 hex digest of ``text`` (lowercase, no salt)."""
    return hashlib.sha256(text.encode()).hexdigest()


def get_system_conf() -> str:
    """Return the ``system.conf`` body, sourced from runtime configuration."""
    return f"""
[System]
Name = ACME Corp Production Server
Environment = Production
Debug = False

[Database]
Host = db.acmecorp.internal
Port = 5432
Database = acme_prod
Username = db_admin
Password = {_resolve("db_password")}

[API]
Gateway = https://api.acmecorp.com
Key = {_resolve("api_gateway_key")}
Secret = {_resolve("api_gateway_secret")}

[AWS]
AccessKeyID = {_resolve("aws_access_key_id")}
SecretAccessKey = {_resolve("aws_secret_access_key")}
Region = us-west-2
"""


def get_tokens() -> dict[str, str]:
    """Return the challenge token map, sourced from the environment."""
    return {
        "admin_token": _resolve("admin_token"),
        "service_token": _resolve("service_token"),
        "user_token": _resolve("user_token"),
    }


def write_tokens(path: str = DEFAULT_TOKENS_PATH) -> str:
    """Materialize ``tokens.json`` at ``path`` and return the written JSON."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(get_tokens(), indent=2)
    target.write_text(content + "\n")
    return content


def get_users() -> dict[str, dict]:
    """Return the demo user database, with hashes sourced from the environment.

    Password *hashes* are derived from runtime plaintext passwords (themselves
    sourced from env vars / safe defaults) via sha256, so no real password hash
    — and no cleartext password hint — is committed to source control.
    """
    return {
        "admin": {
            "username": "admin",
            "password_hash": _sha256(_resolve("admin_password")),
            "role": "admin",
            "email": "admin@acmecorp.com",
        },
        "service": {
            "username": "service",
            "password_hash": _sha256(_resolve("service_password")),
            "role": "service",
            "email": "service@acmecorp.com",
        },
        "user": {
            "username": "user",
            "password_hash": _sha256(_resolve("user_password")),
            "role": "user",
            "email": "user@acmecorp.com",
        },
    }


def write_users(path: str = DEFAULT_USERS_PATH) -> str:
    """Materialize ``users.json`` at ``path`` and return the written JSON."""
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    content = json.dumps(get_users(), indent=2)
    target.write_text(content + "\n")
    return content


def get_admin_dashboard() -> str:
    """Return the admin-dashboard string, sourcing the master password at runtime."""
    return f"""
ADMIN DASHBOARD
--------------
System Status: All services operational
Last Backup: 2025-04-15 03:00 UTC
Security Alerts: None

SENSITIVE INFORMATION:
- Master Password: {_resolve("master_password")}
- Recovery Email: recovery@acmecorp.com
- Emergency Contact: John Doe (555-123-4567)

SYSTEM NOTES:
- Remember to rotate API keys by end of month
- Schedule security audit for next quarter
- Update firewall rules for new office IP range
"""


if __name__ == "__main__":  # pragma: no cover - CLI entry for boot scripts
    print(get_system_conf())
