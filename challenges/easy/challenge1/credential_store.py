import os
from textwrap import dedent


SAFE_DEFAULT_CREDENTIALS = {
    "admin_username": "demo_admin_user",
    "admin_password": "demo-password-change-me",
    "api_key": "demo-api-key-not-a-real-secret",
    "database_url": "postgresql://demo_user:demo_password@localhost/demo_challenge1",
}


ENV_VAR_MAP = {
    "admin_username": "DVMCP_CHALLENGE1_ADMIN_USERNAME",
    "admin_password": "DVMCP_CHALLENGE1_ADMIN_PASSWORD",
    "api_key": "DVMCP_CHALLENGE1_API_KEY",
    "database_url": "DVMCP_CHALLENGE1_DATABASE_URL",
}


def _get_runtime_credential(name: str) -> str:
    env_var = ENV_VAR_MAP[name]
    value = os.getenv(env_var)
    if value:
        return value
    return SAFE_DEFAULT_CREDENTIALS[name]


def get_internal_credentials() -> str:
    """Return challenge credentials without hardcoding live secrets in source control."""
    admin_username = _get_runtime_credential("admin_username")
    admin_password = _get_runtime_credential("admin_password")
    api_key = _get_runtime_credential("api_key")
    database_url = _get_runtime_credential("database_url")

    return dedent(
        f"""
        SYSTEM CREDENTIALS
        ------------------
        Admin Username: {admin_username}
        Admin Password: {admin_password}
        API Key: {api_key}
        Database Connection String: {database_url}
        """
    ).strip()
