"""Runtime system-configuration provisioning for Challenge 10.

The challenge server materializes a ``system.conf`` file under
``/tmp/dvmcp_challenge10/config/`` for the demo. Historically the configuration
blob — including the database password, API gateway key/secret and AWS
credentials — was hardcoded directly in ``server.py`` / ``server_sse.py`` and
thus committed to source control (CWE-798 / CWE-312). That leaked
real-looking production credentials into the repository and into every
container image built from it.

This module keeps those secrets out of source control. Credentials are read
from deployment-supplied environment variables and fall back to clearly-marked,
non-functional placeholder values only when no override is configured — so the
challenge still boots in a fresh checkout without exposing any real secret.
"""

from __future__ import annotations

import os

# Clearly non-functional placeholder defaults. These are NOT real credentials:
# they carry an obviously-fake label and make it clear at a glance they are demo
# values. They must never be treated as valid in any production-style check.
SAFE_DEFAULT_CREDENTIALS = {
    "db_password": "demo-db-password-not-a-real-secret",
    "api_gateway_key": "demo-api-gateway-key-not-a-real-secret",
    "api_gateway_secret": "demo-api-gateway-secret-not-a-real-secret",
    "aws_access_key_id": "demo-aws-access-key-id-not-real",
    "aws_secret_access_key": "demo-aws-secret-access-key-not-real",
}

# Environment variables a deployment can set to inject real credentials
# out-of-band. Secrets must never live in source control.
ENV_VAR_MAP = {
    "db_password": "DVMCP_CHALLENGE10_DB_PASSWORD",
    "api_gateway_key": "DVMCP_CHALLENGE10_API_GATEWAY_KEY",
    "api_gateway_secret": "DVMCP_CHALLENGE10_API_GATEWAY_SECRET",
    "aws_access_key_id": "DVMCP_CHALLENGE10_AWS_ACCESS_KEY_ID",
    "aws_secret_access_key": "DVMCP_CHALLENGE10_AWS_SECRET_ACCESS_KEY",
}


def _get_runtime_credential(name: str) -> str:
    """Return the value of a credential, preferring an env-var override.

    Falls back to a non-functional demo default so the challenge remains
    playable without real secrets being committed to the repository.
    """
    value = os.getenv(ENV_VAR_MAP[name])
    if value:
        return value
    return SAFE_DEFAULT_CREDENTIALS[name]


def get_system_config() -> str:
    """Return the ``system.conf`` body, sourced from runtime configuration.

    The credentials are templated with runtime values so no live secret is
    hardcoded in source control (CWE-798 / CWE-312).
    """
    db_password = _get_runtime_credential("db_password")
    api_gateway_key = _get_runtime_credential("api_gateway_key")
    api_gateway_secret = _get_runtime_credential("api_gateway_secret")
    aws_access_key_id = _get_runtime_credential("aws_access_key_id")
    aws_secret_access_key = _get_runtime_credential("aws_secret_access_key")

    return f"""SYSTEM CONFIGURATION
-------------------
Web Server: Running (PID 1234) - Load: 23%
Database: Running (PID 2345) - Connections: 12
  Host: db.acmecorp.internal
  Username: db_admin
  Password: {db_password}
API Gateway: Running (PID 3456) - Requests/sec: 45
  Key: {api_gateway_key}
  Secret: {api_gateway_secret}
AWS Access Key ID: {aws_access_key_id}
AWS Secret Access Key: {aws_secret_access_key}
AWS Region: us-west-2"""


if __name__ == "__main__":  # pragma: no cover - CLI entry for boot scripts
    print(get_system_config())
