import os


# ---------------------------------------------------------------------------
# Token storage for Challenge 7.
#
# The previous implementation hardcoded live-looking API keys, JWT access
# tokens and refresh tokens directly in server.py. Those values were committed
# to source control (CWE-798 / CWE-312). They have been removed from source and
# replaced with clearly-marked, non-functional demo values that can be
# overridden at runtime via the DVMCP_CHALLENGE7_* environment variables.
# ---------------------------------------------------------------------------

# Safe, non-functional demo defaults. These are intentionally fake-looking so
# the challenge remains runnable in a sandbox/lab without shipping real
# secrets in source control.
SAFE_DEFAULT_TOKENS = {
    "email_service": {
        "service_name": "EmailPro API",
        "api_key": "demo-email-api-key-not-a-real-secret",
        "access_token": "demo-email-access-token-not-a-real-secret",
        "refresh_token": "demo-email-refresh-token-not-a-real-secret",
        "expires_at": "2025-12-31T23:59:59Z",
    },
    "cloud_storage": {
        "service_name": "CloudBox Storage",
        "api_key": "demo-storage-api-key-not-a-real-secret",
        "access_token": "demo-storage-access-token-not-a-real-secret",
        "refresh_token": "demo-storage-refresh-token-not-a-real-secret",
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


# Per-field environment variable overrides. Operators deploy real secrets
# through these rather than embedding them in the repository.
ENV_VAR_MAP = {
    ("email_service", "api_key"): "DVMCP_CHALLENGE7_EMAIL_API_KEY",
    ("email_service", "access_token"): "DVMCP_CHALLENGE7_EMAIL_ACCESS_TOKEN",
    ("email_service", "refresh_token"): "DVMCP_CHALLENGE7_EMAIL_REFRESH_TOKEN",
    ("cloud_storage", "api_key"): "DVMCP_CHALLENGE7_STORAGE_API_KEY",
    ("cloud_storage", "access_token"): "DVMCP_CHALLENGE7_STORAGE_ACCESS_TOKEN",
    ("cloud_storage", "refresh_token"): "DVMCP_CHALLENGE7_STORAGE_REFRESH_TOKEN",
    ("analytics_platform", "api_key"): "DVMCP_CHALLENGE7_ANALYTICS_API_KEY",
    ("analytics_platform", "access_token"): "DVMCP_CHALLENGE7_ANALYTICS_ACCESS_TOKEN",
    ("analytics_platform", "refresh_token"): "DVMCP_CHALLENGE7_ANALYTICS_REFRESH_TOKEN",
}


def _resolve(service_id: str, field: str) -> str:
    """Return the runtime value for a (service, field), falling back to the
    safe demo default when no environment variable is set."""
    env_value = os.getenv(ENV_VAR_MAP[(service_id, field)])
    if env_value:
        return env_value
    return SAFE_DEFAULT_TOKENS[service_id][field]


def get_tokens() -> dict:
    """Return the token store for the integrated services without hardcoding
    live secrets in source control."""
    tokens = {}
    for service_id, defaults in SAFE_DEFAULT_TOKENS.items():
        tokens[service_id] = {
            "service_name": defaults["service_name"],
            "api_key": _resolve(service_id, "api_key"),
            "access_token": _resolve(service_id, "access_token"),
            "refresh_token": _resolve(service_id, "refresh_token"),
            "expires_at": defaults["expires_at"],
        }
    return tokens


# Safe, non-functional demo default for the admin API token used by the SSE
# server. Overridable at runtime via DVMCP_CHALLENGE7_ADMIN_API_TOKEN.
ADMIN_API_TOKEN_DEFAULT = "demo-admin-api-token-not-a-real-secret"


def get_admin_api_token() -> str:
    """Return the admin API token without hardcoding a live secret in source
    control."""
    return os.getenv("DVMCP_CHALLENGE7_ADMIN_API_TOKEN", ADMIN_API_TOKEN_DEFAULT)
