"""Runtime secret + context provisioning for Challenge 9.

Challenge 9 (Context Injection & Over-Sharing) deliberately seeds an in-memory
"shared context" with notes that include real-looking production secrets
directly in source control (CWE-798 / CWE-312):

  * a production database password
  * an API key

The challenge's pedagogical point is that the MCP server keeps this context
*global* across sessions and exposes a search tool with no authorization
check, so one user can read another user's notes (including the admin/system
notes). We keep that vulnerable shape intact while moving the actual secret
*values* out of source control: secrets are sourced from deployment-supplied
environment variables and fall back to clearly-marked, non-functional
placeholder values only when no override is configured.

This preserves the documented challenge behavior (admin/system notes exist and
are exfiltrable via the unauthenticated search tool) without shipping real
secrets in the repository.
"""

from __future__ import annotations

import os
import time

# Placeholder values used only when no runtime secret is supplied. These are
# deliberately non-secret, non-functional values so the challenge can run in a
# development environment without exposing real credentials in source control.
_SAFE_DEFAULTS = {
    "db_password": "demo-db-password-not-a-real-secret",
    "api_key": "demo-api-key-not-a-real-secret",
}

# Mapping from logical secret name to the environment variable that supplies
# the real value in a deployment.
_ENV_VAR_MAP = {
    "db_password": "DVMCP_CHALLENGE9_DB_PASSWORD",
    "api_key": "DVMCP_CHALLENGE9_API_KEY",
}


def _get_runtime_secret(name: str) -> str:
    """Return a secret from the environment, falling back to a safe default."""
    value = os.getenv(_ENV_VAR_MAP[name])
    if value:
        return value
    return _SAFE_DEFAULTS[name]


def build_initial_shared_context() -> dict:
    """Return the seeded shared-context dict, without hardcoding live secrets.

    The shape (an ``admin`` list and a ``system`` list of timestamped notes) is
    preserved exactly so the challenge's documented exploitation path still
    works. Only the secret *values* are sourced from the environment.
    """
    db_password = _get_runtime_secret("db_password")
    api_key = _get_runtime_secret("api_key")

    return {
        "admin": [
            {
                "timestamp": int(time.time()) - 3600,
                "note": f"Reminder: The production database password for the new cluster is {db_password}",
            },
            {
                "timestamp": int(time.time()) - 1800,
                "note": "Meeting with security team at 2 PM to discuss the recent audit findings.",
            },
        ],
        "system": [
            {
                "timestamp": int(time.time()) - 86400,
                "note": "Server initialized successfully. API key loaded into memory.",
            },
            {
                "timestamp": int(time.time()) - 86399,
                "note": f"API_KEY={api_key}",
            },
        ],
    }
