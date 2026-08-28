"""Runtime credential provisioning for Challenge 8.

Challenge 8 (Malicious Code Execution) exposes a ``credentials.txt`` file at
``/tmp/dvmcp_challenge8/sensitive/credentials.txt`` that a learner reads via
the vulnerable code-execution tool. Historically this file — and the boot
script ``startup.sh`` that seeds it — embedded real-looking production secrets
directly in source control (CWE-798 / CWE-312):

  * a database password
  * an AWS access key id + secret access key
  * an API Gateway key + secret

This module keeps those values out of source control. Secrets are read from
deployment-supplied environment variables and fall back to clearly-marked,
non-functional placeholder values only when no override is configured — so the
challenge still boots in a fresh checkout without exposing any real secret.

The on-disk file shape is preserved exactly so existing challenge tooling
(including the documented solution path that reads
``/tmp/dvmcp_challenge8/sensitive/credentials.txt``) keeps working.
"""

from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent

# Path written by startup.sh / the server on boot.
DEFAULT_CREDENTIALS_PATH = "/tmp/dvmcp_challenge8/sensitive/credentials.txt"

# Placeholder values used only when no runtime secret is supplied. These are
# deliberately non-secret, non-functional values so the challenge can run in a
# development environment without shipping real credentials in source control.
_SAFE_DEFAULTS = {
    "db_password": "demo-db-password-not-a-real-secret",
    "aws_access_key_id": "AKIADemoAccessKeyNotReal",
    "aws_secret_access_key": "demo-aws-secret-access-key-not-a-real-secret",
    "api_gateway_key": "demo-api-gateway-key-not-a-real-secret",
    "api_gateway_secret": "demo-api-gateway-secret-not-a-real-secret",
}

# Mapping from logical secret name to the environment variable that supplies
# the real value in a deployment.
_ENV_VAR_MAP = {
    "db_password": "DVMCP_CHALLENGE8_DB_PASSWORD",
    "aws_access_key_id": "DVMCP_CHALLENGE8_AWS_ACCESS_KEY_ID",
    "aws_secret_access_key": "DVMCP_CHALLENGE8_AWS_SECRET_ACCESS_KEY",
    "api_gateway_key": "DVMCP_CHALLENGE8_API_GATEWAY_KEY",
    "api_gateway_secret": "DVMCP_CHALLENGE8_API_GATEWAY_SECRET",
}


def _get_runtime_secret(name: str) -> str:
    """Return a secret from the environment, falling back to a safe default."""
    value = os.getenv(_ENV_VAR_MAP[name])
    if value:
        return value
    return _SAFE_DEFAULTS[name]


def get_credentials() -> str:
    """Return the credentials.txt content without hardcoding live secrets.

    Non-secret operational config (database host/username, AWS region) stays
    inline because it is not a credential; every actual secret is sourced from
    the environment via ``DVMCP_CHALLENGE8_*`` with a safe placeholder default.
    """
    db_password = _get_runtime_secret("db_password")
    aws_access_key_id = _get_runtime_secret("aws_access_key_id")
    aws_secret_access_key = _get_runtime_secret("aws_secret_access_key")
    api_gateway_key = _get_runtime_secret("api_gateway_key")
    api_gateway_secret = _get_runtime_secret("api_gateway_secret")

    return dedent(
        f"""
        PRODUCTION CREDENTIALS
        ----------------------
        Database:
          Host: db.acmecorp.internal
          Username: db_admin
          Password: {db_password}

        AWS:
          Access Key ID: {aws_access_key_id}
          Secret Access Key: {aws_secret_access_key}
          Region: us-west-2

        API Gateway:
          Key: {api_gateway_key}
          Secret: {api_gateway_secret}
        """
    ).strip() + "\n"


def write_credentials(path: str = DEFAULT_CREDENTIALS_PATH) -> str:
    """Materialize ``credentials.txt`` at ``path`` and return the written text.

    The directory is created if needed. The on-disk content mirrors the
    previous shape of the file so existing challenge tooling keeps working.
    """
    target = Path(path)
    target.parent.mkdir(parents=True, exist_ok=True)
    content = get_credentials()
    target.write_text(content)
    return content


if __name__ == "__main__":  # pragma: no cover - CLI entry for startup.sh
    import sys

    # Allow:  python -m challenges.hard.challenge8.credential_store write_credentials
    # or:     python challenges/hard/challenge8/credential_store.py
    if len(sys.argv) > 1 and sys.argv[1] not in ("write_credentials",):
        sys.exit(f"Unknown command: {sys.argv[1]}")
    print(write_credentials(), end="")
