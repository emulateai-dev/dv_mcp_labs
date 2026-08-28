"""Runtime credential provisioning for Challenge 9.

Challenge 9 (Context Injection & Over-Sharing) deliberately exposes
``admin`` and ``system`` context notes through the MCP tool surface so a
learner can observe the cross-session data leak. Historically the seeded
notes embedded real-looking production secrets directly in source control
(CWE-798 / CWE-312):

  * a production database password (previously embedded verbatim)
  * an API key (previously embedded verbatim)

Anyone with read access to the repo or a built container image recovered
those secret values without ever interacting with the running service.

This module keeps those values out of source control. Each secret is read
from a deployment-supplied environment variable and falls back to a
clearly-marked, non-functional placeholder value only when no override is
configured — so the challenge still boots in a fresh checkout without
exposing any real secret, and the documented solution path (querying the AI
to extract cross-session context) keeps working unchanged.
"""

from __future__ import annotations

import os
from typing import Dict, List


# Placeholder values used only when no runtime secret is supplied. These are
# deliberately non-secret, non-functional values so the challenge can run in a
# development environment without shipping real credentials in source control.
_SAFE_DEFAULTS = {
    "admin_note": "Reminder: The production database password is configured via the DVMCP_CHALLENGE9_ADMIN_DB_PASSWORD environment variable.",
    "system_note": "API_KEY configured via the DVMCP_CHALLENGE9_SYSTEM_API_KEY environment variable.",
}

# Mapping from logical secret name to the environment variable that supplies
# the real value in a deployment.
_ENV_VAR_MAP = {
    "admin_note": "DVMCP_CHALLENGE9_ADMIN_DB_PASSWORD",
    "system_note": "DVMCP_CHALLENGE9_SYSTEM_API_KEY",
}


def _get_runtime_secret(name: str, value: str | None = None) -> str:
    """Return a secret from the environment, falling back to a safe default.

    If ``value`` is provided it is used verbatim (callers may pass an explicit
    secret); otherwise the relevant ``DVMCP_CHALLENGE9_*`` env var is consulted
    and, when unset, the non-functional placeholder default is returned.
    """
    if value is not None and value.strip():
        return value
    env_value = os.getenv(_ENV_VAR_MAP[name])
    if env_value and env_value.strip():
        return env_value.strip()
    return _SAFE_DEFAULTS[name]


def _format_db_password_note(password: str | None = None) -> str:
    """Build the seeded admin reminder note without hardcoding the secret."""
    secret = _get_runtime_secret("admin_note", password)
    return f"Reminder: The production database password for the new cluster is {secret}"


def _format_api_key_note(api_key: str | None = None) -> str:
    """Build the seeded system API key note without hardcoding the secret."""
    secret = _get_runtime_secret("system_note", api_key)
    return f"API_KEY={secret}"


def build_shared_context(
    now: int | None = None,
    admin_db_password: str | None = None,
    system_api_key: str | None = None,
) -> Dict[str, List[Dict[str, int | str]]]:
    """Construct the SHARED_CONTEXT seed dict used by the Challenge 9 server.

    The dict shape (per-user lists of ``{"timestamp", "note"}`` entries) is
    preserved exactly so existing challenge tooling — including the documented
    solution path that reads the AI's cross-session context — keeps working.

    ``now`` is an optional Unix timestamp used for the note timestamps so tests
    can assert deterministic ordering; when omitted the current time is used.
    """
    import time

    current = int(time.time()) if now is None else int(now)

    return {
        "admin": [
            {
                "timestamp": current - 3600,
                "note": _format_db_password_note(admin_db_password),
            },
            {
                "timestamp": current - 1800,
                "note": "Meeting with security team at 2 PM to discuss the recent audit findings.",
            },
        ],
        "system": [
            {
                "timestamp": current - 86400,
                "note": "Server initialized successfully. API key loaded into memory.",
            },
            {
                "timestamp": current - 86399,
                "note": _format_api_key_note(system_api_key),
            },
        ],
    }


__all__ = ["build_shared_context"]
