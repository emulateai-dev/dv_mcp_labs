"""Runtime credential provisioning for Challenge 10.

The challenge server materializes a ``system.conf`` file (read by the shadow
``analyze_log_file`` tool) that historically embedded real-looking production
secrets directly in source control (CWE-798 / CWE-312): a database password,
an API gateway key + secret, and AWS access key ID + secret access key. Anyone
with read access to the repository — or to a container image built from it —
recovered those secrets.

This module keeps operational credentials out of source control. Real values
are read from deployment-supplied environment variables; when unset, clearly
marked, non-functional placeholder values are used so the challenge still boots
from a fresh checkout without leaking any secret.
"""

from __future__ import annotations

import os
from textwrap import dedent

# Placeholder values used only when no runtime secret is supplied. These are
# deliberately non-secret, non-functional values so the challenge runs in a
# development environment without shipping real credentials in source control.
SAFE_DEFAULT_CREDENTIALS = {
    "db_password": "demo-db-password-not-a-real-secret",
    "api_gateway_key": "demo-api-gateway-key-not-a-real-secret",
    "api_gateway_secret": "demo-api-gateway-secret-not-a-real-secret",
    "aws_access_key_id": "demo-aws-access-key-id-not-a-real-secret",
    "aws_secret_access_key": "demo-aws-secret-access-key-not-a-real-secret",
}

# Mapping from logical credential name to the environment variable that
# supplies the real value in a deployment.
ENV_VAR_MAP = {
    "db_password": "DVMCP_CHALLENGE10_DB_PASSWORD",
    "api_gateway_key": "DVMCP_CHALLENGE10_API_GATEWAY_KEY",
    "api_gateway_secret": "DVMCP_CHALLENGE10_API_GATEWAY_SECRET",
    "aws_access_key_id": "DVMCP_CHALLENGE10_AWS_ACCESS_KEY_ID",
    "aws_secret_access_key": "DVMCP_CHALLENGE10_AWS_SECRET_ACCESS_KEY",
}


def _get_runtime_credential(name: str) -> str:
    """Return a credential from the environment, falling back to a safe default."""
    value = os.getenv(ENV_VAR_MAP[name])
    if value:
        return value
    return SAFE_DEFAULT_CREDENTIALS[name]


def get_credentials() -> dict[str, str]:
    """Return the Challenge 10 credential map, sourced from the environment.

    Real credentials are injected via the ``DVMCP_CHALLENGE10_*`` environment
    variables by the deployment. When unset, non-functional placeholder values
    are used so the demo boots without leaking secrets in source control.
    """
    return {name: _get_runtime_credential(name) for name in ENV_VAR_MAP}


def get_system_conf() -> str:
    """Return ``system.conf`` content without hardcoding live secrets in source."""
    creds = get_credentials()
    return dedent(
        f"""
        SYSTEM CONFIGURATION
        -------------------
        Web Server: Running (PID 1234) - Load: 23%
        Database: Running (PID 2345) - Connections: 12
          Host: db.acmecorp.internal
          Username: db_admin
          Password: {creds['db_password']}
        API Gateway: Running (PID 3456) - Requests/sec: 45
          Key: {creds['api_gateway_key']}
          Secret: {creds['api_gateway_secret']}
        AWS Access Key ID: {creds['aws_access_key_id']}
        AWS Secret Access Key: {creds['aws_secret_access_key']}
        AWS Region: us-west-2
        """
    ).strip()
