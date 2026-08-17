import os

# ---------------------------------------------------------------------------
# Credential store for Challenge 7 (SSE server).
#
# The previous implementation hardcoded a long-lived admin API token directly
# in challenges/medium/challenge7/server_sse.py (including a copy embedded in
# the `authenticate` tool docstring, which leaks into the MCP context window)
# and hardcoded additional "system secrets" (DB password, internal API key,
# S3 bucket name) in the `access_admin_panel` tool output. Those values were
# committed to source control (CWE-798 "Use of Hard-coded Credentials" /
# CWE-312 "Cleartext Storage of Sensitive Information").
#
# They have been removed from source and replaced with clearly-marked,
# non-functional demo defaults that operators override at runtime through the
# DVMCP_CHALLENGE7_* environment variables. No live secret is shipped in the
# repository.
# ---------------------------------------------------------------------------

# Safe, non-functional demo defaults. Intentionally fake-looking so the
# challenge remains runnable in a sandbox/lab without embedding real secrets.
ADMIN_API_TOKEN_DEFAULT = "demo-admin-api-token-not-a-real-secret"
ADMIN_DB_PASSWORD_DEFAULT = "demo-db-password-not-a-real-secret"
ADMIN_INTERNAL_API_KEY_DEFAULT = "demo-internal-api-key-not-a-real-secret"
ADMIN_S3_BUCKET_DEFAULT = "demo-s3-bucket-not-a-real-bucket"


def get_admin_api_token() -> str:
    """Return the admin API token, sourced from the environment so no live
    secret is hardcoded in source control (CWE-798 / CWE-312)."""
    return os.getenv("DVMCP_CHALLENGE7_ADMIN_API_TOKEN", ADMIN_API_TOKEN_DEFAULT)


def get_admin_system_secrets() -> dict:
    """Return the admin panel "system secrets" without hardcoding live
    values in source control (CWE-798 / CWE-312). Each field is overridable
    at runtime via its own DVMCP_CHALLENGE7_* environment variable."""
    return {
        "DB_PASSWORD": os.getenv(
            "DVMCP_CHALLENGE7_ADMIN_DB_PASSWORD", ADMIN_DB_PASSWORD_DEFAULT
        ),
        "INTERNAL_API_KEY": os.getenv(
            "DVMCP_CHALLENGE7_ADMIN_INTERNAL_API_KEY", ADMIN_INTERNAL_API_KEY_DEFAULT
        ),
        "S3_BUCKET": os.getenv(
            "DVMCP_CHALLENGE7_ADMIN_S3_BUCKET", ADMIN_S3_BUCKET_DEFAULT
        ),
    }
