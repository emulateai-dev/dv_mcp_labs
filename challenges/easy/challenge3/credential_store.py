"""Runtime credential provisioning for Challenge 3.

Challenge 3 (Excessive Permission Scope) exposes a ``system_credentials.txt``
file at ``/tmp/dvmcp_challenge3/private/system_credentials.txt`` that a learner
reaches via the vulnerable file-manager / read_file tools. Historically this
file — and the boot scripts (``startup.sh``, ``start_sse_servers.sh``) plus the
non-SSE server (``challenges/easy/challenge3/server.py``) that seed it — embedded
real-looking production secrets directly in source control (CWE-798 / CWE-312):

  * a database password (Pr0d-DB-S3cret!)
  * an account id (ACME-CLOUD-92731)
  * a cloud API key (ak_live_7y2JHGd8sKlM9nPzXqRt5vWx)
  * a cloud API secret (cs_live_bNp5T2vR8sKlM9nQzXwJhGf4)

This module keeps those values out of source control. Secrets are read from
deployment-supplied environment variables and fall back to clearly-marked,
non-functional placeholder values only when no override is configured — so the
challenge still boots in a fresh checkout without exposing any real secret.

The on-disk file shape is preserved exactly so existing challenge tooling
(including the documented solution path that reads
``/tmp/dvmcp_challenge3/private/system_credentials.txt``) keeps working.
"""

from __future__ import annotations

import os
from pathlib import Path
from textwrap import dedent

# Path written by startup.sh / start_sse_servers.sh / server.py on boot.
DEFAULT_CREDENTIALS_PATH = "/tmp/dvmcp_challenge3/private/system_credentials.txt"

# Placeholder values used only when no runtime secret is supplied. These are
# deliberately non-secret, non-functional values so the challenge can run in a
# development environment without shipping real credentials in source control.
_SAFE_DEFAULTS = {
    "db_password": "demo-db-password-not-a-real-secret",
    "cloud_account_id": "ACME-DEMO-CLOUD-NOT-REAL",
    "cloud_api_key": "ak_demo_NotARealApiKey0123456789",
    "cloud_api_secret": "cs_demo_NotARealSecret0123456789abcdef",
}

# Mapping from logical secret name to the environment variable that supplies
# the real value in a deployment.
_ENV_VAR_MAP = {
    "db_password": "DVMCP_CHALLENGE3_DB_PASSWORD",
    "cloud_account_id": "DVMCP_CHALLENGE3_CLOUD_ACCOUNT_ID",
    "cloud_api_key": "DVMCP_CHALLENGE3_CLOUD_API_KEY",
    "cloud_api_secret": "DVMCP_CHALLENGE3_CLOUD_API_SECRET",
}


def _get_runtime_secret(name: str) -> str:
    """Return a secret from the environment, falling back to a safe default."""
    value = os.getenv(_ENV_VAR_MAP[name])
    if value:
        return value
    return _SAFE_DEFAULTS[name]


def get_credentials() -> str:
    """Return the system_credentials.txt content without hardcoding live secrets.

    Non-secret operational config (database host/username) stays inline because
    it is not a credential; every actual secret is sourced from the environment
    via ``DVMCP_CHALLENGE3_*`` with a safe placeholder default.
    """
    db_password = _get_runtime_secret("db_password")
    cloud_account_id = _get_runtime_secret("cloud_account_id")
    cloud_api_key = _get_runtime_secret("cloud_api_key")
    cloud_api_secret = _get_runtime_secret("cloud_api_secret")

    return dedent(
        f"""
        SYSTEM CREDENTIALS - HIGHLY RESTRICTED
        -------------------------------------
        Production Database:
          Host: db.acmecorp.internal
          Username: admin_prod
          Password: {db_password}

        Cloud Infrastructure:
          Account ID: {cloud_account_id}
          API Key: {cloud_api_key}
          Secret: {cloud_api_secret}
        """
    ).strip() + "\n"


def write_credentials(path: str = DEFAULT_CREDENTIALS_PATH) -> str:
    """Materialize ``system_credentials.txt`` at ``path`` and return the text.

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

    # Allow:  python -m challenges.easy.challenge3.credential_store write_credentials
    # or:     python challenges/easy/challenge3/credential_store.py
    if len(sys.argv) > 1 and sys.argv[1] not in ("write_credentials",):
        sys.exit(f"Unknown command: {sys.argv[1]}")
    print(write_credentials(), end="")
