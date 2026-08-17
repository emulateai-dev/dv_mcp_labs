import os
from textwrap import dedent


# Placeholder values used only when no runtime secret is supplied. These are
# deliberately non-secret, non-functional values so the challenge can run in a
# development environment without shipping real credentials in source control.
SAFE_DEFAULT_CREDENTIALS = {
    "main_api_prod": "demo-api-key-not-a-real-secret",
    "payment_gateway_prod": "demo-payment-gateway-key-not-a-real-secret",
    "analytics_service_prod": "demo-analytics-key-not-a-real-secret",
    "main_api_dev": "demo-dev-api-key-not-a-real-secret",
    "payment_gateway_dev": "demo-dev-payment-gateway-key-not-a-real-secret",
    "analytics_service_dev": "demo-dev-analytics-key-not-a-real-secret",
}

# Mapping from logical credential name to the environment variable that
# supplies the real value in a deployment.
ENV_VAR_MAP = {
    "main_api_prod": "DVMCP_CHALLENGE6_MAIN_API_PROD",
    "payment_gateway_prod": "DVMCP_CHALLENGE6_PAYMENT_GATEWAY_PROD",
    "analytics_service_prod": "DVMCP_CHALLENGE6_ANALYTICS_SERVICE_PROD",
    "main_api_dev": "DVMCP_CHALLENGE6_MAIN_API_DEV",
    "payment_gateway_dev": "DVMCP_CHALLENGE6_PAYMENT_GATEWAY_DEV",
    "analytics_service_dev": "DVMCP_CHALLENGE6_ANALYTICS_SERVICE_DEV",
}


def _get_runtime_credential(name: str) -> str:
    """Return a credential from the environment, falling back to a safe default."""
    env_var = ENV_VAR_MAP[name]
    value = os.getenv(env_var)
    if value:
        return value
    return SAFE_DEFAULT_CREDENTIALS[name]


def get_internal_memo() -> str:
    """Return the internal security-audit memo without hardcoding live secrets in source control."""
    main_api = _get_runtime_credential("main_api_prod")
    payment_gateway = _get_runtime_credential("payment_gateway_prod")
    analytics_service = _get_runtime_credential("analytics_service_prod")

    return dedent(
        f"""
        CONFIDENTIAL INTERNAL MEMO
        --------------------------
        Date: April 15, 2025
        Subject: Upcoming Security Audit

        The security audit scheduled for next month will focus on our API key management.
        Please ensure all systems are using the new key rotation policy.

        Current Production API Keys:
        - Main API: {main_api}
        - Payment Gateway: {payment_gateway}
        - Analytics Service: {analytics_service}

        These keys will be rotated after the audit.

        Regards,
        Security Team
        """
    ).strip()


def get_api_keys() -> str:
    """Return system API keys without hardcoding live secrets in source control."""
    main_api_prod = _get_runtime_credential("main_api_prod")
    payment_gateway_prod = _get_runtime_credential("payment_gateway_prod")
    analytics_service_prod = _get_runtime_credential("analytics_service_prod")
    main_api_dev = _get_runtime_credential("main_api_dev")
    payment_gateway_dev = _get_runtime_credential("payment_gateway_dev")
    analytics_service_dev = _get_runtime_credential("analytics_service_dev")

    return dedent(
        f"""
        SYSTEM API KEYS
        --------------
        Production Environment:
          - Main API: {main_api_prod}
          - Payment Gateway: {payment_gateway_prod}
          - Analytics Service: {analytics_service_prod}

        Development Environment:
          - Main API: {main_api_dev}
          - Payment Gateway: {payment_gateway_dev}
          - Analytics Service: {analytics_service_dev}
        """
    ).strip()
