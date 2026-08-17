import os
from textwrap import dedent


# Placeholder values used only when no runtime secret is supplied. These are
# deliberately non-secret, non-functional values so the challenge can run in a
# development environment without shipping real credentials in source control.
SAFE_DEFAULT_SECRETS = {
    "database_password": "demo-db-password-change-me",
    "admin_username": "demo_admin@example.com",
    "admin_password": "demo-admin-password-change-me",
    "api_key": "demo-api-key-not-a-real-secret",
    "encryption_key": "0" * 32,
}

ENV_VAR_MAP = {
    "database_password": "DVMCP_CHALLENGE5_DATABASE_PASSWORD",
    "admin_username": "DVMCP_CHALLENGE5_ADMIN_USERNAME",
    "admin_password": "DVMCP_CHALLENGE5_ADMIN_PASSWORD",
    "api_key": "DVMCP_CHALLENGE5_API_KEY",
    "encryption_key": "DVMCP_CHALLENGE5_ENCRYPTION_KEY",
}


def _get_runtime_secret(name: str) -> str:
    """Return a secret from the environment, falling back to a safe default."""
    env_var = ENV_VAR_MAP[name]
    value = os.getenv(env_var)
    if value:
        return value
    return SAFE_DEFAULT_SECRETS[name]


def get_system_secrets() -> str:
    """Return the challenge's system secrets without hardcoding live values.

    The values are sourced from environment variables so that real deployments
    inject their own secrets at runtime; the in-source defaults are clearly
    non-functional placeholders that are safe to commit.
    """
    database_password = _get_runtime_secret("database_password")
    admin_username = _get_runtime_secret("admin_username")
    admin_password = _get_runtime_secret("admin_password")
    api_key = _get_runtime_secret("api_key")
    encryption_key = _get_runtime_secret("encryption_key")

    return dedent(
        f"""
        SYSTEM SECRETS
        --------------
        Database Password: {database_password}
        Admin Account: {admin_username} / {admin_password}
        API Key: {api_key}
        Encryption Key: {encryption_key}
        """
    ).strip()
