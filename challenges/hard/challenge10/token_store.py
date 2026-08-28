"""Runtime token provisioning for Challenge 10.

The challenge server (and the boot script ``start_sse_servers.sh``) both need
to materialize a ``tokens.json`` file for the demo. Historically this file was
seeded with hardcoded JWTs checked into source control (CWE-798 / CWE-312),
which leaked real-looking admin/service/user tokens into the repository and
into every container image built from it.

This module keeps operational tokens out of source control. Tokens are read
from deployment-supplied environment variables and fall back to clearly-marked,
non-functional placeholder values only when no override is configured — so the
challenge still boots in a fresh checkout without exposing any real secret.
"""

from __future__ import annotations

import json
import os
from pathlib import Path

# Default placeholder tokens. These are NOT real credentials: they carry an
# obviously-fake subject and a deterministic, unforgeable-looking suffix that
# makes it clear at a glance they are demo values. They must never be treated
# as valid in any production-style check.
_DEFAULT_ADMIN_TOKEN = "demo-admin-token-not-a-real-secret"
_DEFAULT_SERVICE_TOKEN = "demo-service-token-not-a-real-secret"
_DEFAULT_USER_TOKEN = "demo-user-token-not-a-real-secret"

# Environment variables a deployment can set to inject real tokens out-of-band.
_ENV_ADMIN_TOKEN = "DVMCP_CHALLENGE10_ADMIN_TOKEN"
_ENV_SERVICE_TOKEN = "DVMCP_CHALLENGE10_SERVICE_TOKEN"
_ENV_USER_TOKEN = "DVMCP_CHALLENGE10_USER_TOKEN"

DEFAULT_TOKENS_PATH = "/tmp/dvmcp_challenge10/config/tokens.json"


def _resolve(env_var: str, default: str) -> str:
    """Return the configured token, or a safe placeholder default."""
    value = os.getenv(env_var, "").strip()
    return value or default


def get_tokens() -> dict[str, str]:
    """Return the challenge token map, sourced from the environment.

    Real tokens are injected via ``DVMCP_CHALLENGE10_*_TOKEN`` environment
    variables by the deployment. When unset, non-functional placeholder values
    are used so the demo still boots without leaking secrets in source control.
    """
    return {
        "admin_token": _resolve(_ENV_ADMIN_TOKEN, _DEFAULT_ADMIN_TOKEN),
        "service_token": _resolve(_ENV_SERVICE_TOKEN, _DEFAULT_SERVICE_TOKEN),
        "user_token": _resolve(_ENV_USER_TOKEN, _DEFAULT_USER_TOKEN),
    }


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


if __name__ == "__main__":  # pragma: no cover - CLI entry for start_sse_servers.sh
    import sys
    # Allow:  python -m challenges.hard.challenge10.token_store write_tokens
    # or:     python challenges/hard/challenge10/token_store.py
    if len(sys.argv) > 1 and sys.argv[1] not in ("write_tokens",):
        sys.exit(f"Unknown command: {sys.argv[1]}")
    print(write_tokens())
