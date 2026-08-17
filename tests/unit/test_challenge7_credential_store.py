import json
import os
import unittest
from unittest.mock import patch

from challenges.medium.challenge7.credential_store import (
    get_tokens,
    get_admin_api_token,
    ADMIN_API_TOKEN_DEFAULT,
    SAFE_DEFAULT_TOKENS,
)


# The live values reported by the finding must never be shipped in source.
_REPORTED_LIVE_SECRETS = [
    "epro_api_5f4e3d2c1b0a9z8y7x",
    "cbx_api_1a2b3c4d5e6f7g8h9i",
    "dm_api_9z8y7x6w5v4u3t2s1r",
    "rt_7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g0f",
    "rt_9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m",
    "rt_3e4r5t6y7u8i9o0p1a2s3d4f5g6h7j",
    # Full JWT access tokens reported in the finding.
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFDTUUgQ29ycCIsImVtYWlsX2FjY2VzcyI6InRydWUiLCJpYXQiOjE2NTE4ODQ4MDB9.5TxfEAVbZRGbKnXaL9Lrx9NqXSNFw2ac4FDzPHvRzSQ",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwibmFtZSI6IkFDTUUgQ29ycCIsInN0b3JhZ2VfYWNjZXNzIjoidHJ1ZSIsImlhdCI6MTY1MTg4NDgwMH0.8FhJ7Z5KFUEJFoQW2xeUL9_NOzlKB3j8fKvxU_5qB4Y",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NDMyMTA5ODc2IiwibmFtZSI6IkFDTUUgQ29ycCIsImFuYWx5dGljc19hY2Nlc3MiOiJ0cnVlIiwiaWF0IjoxNjUxODg0ODAwfQ.QzHJ2_8NXiPd5Vl6r3S1VJqFaC3-U_a9FPRJXBgU8Pg",
    # Hardcoded admin API token from the SSE server.
    "mcp-admin-9f8e7d6c5b4a3210",
]


class Challenge7CredentialStoreTests(unittest.TestCase):
    def test_safe_defaults_do_not_ship_the_reported_live_secret_values(self):
        tokens = get_tokens()
        blob = json.dumps(tokens)

        for secret in _REPORTED_LIVE_SECRETS:
            self.assertNotIn(
                secret, blob, f"Live secret {secret!r} must not be in defaults"
            )

        # Safe demo placeholders should be present instead.
        self.assertEqual(
            tokens["email_service"]["api_key"], "demo-email-api-key-not-a-real-secret"
        )
        self.assertEqual(
            tokens["cloud_storage"]["api_key"], "demo-storage-api-key-not-a-real-secret"
        )
        self.assertEqual(
            tokens["analytics_platform"]["api_key"],
            "demo-analytics-api-key-not-a-real-secret",
        )

    def test_admin_token_default_does_not_ship_live_secret(self):
        token = get_admin_api_token()
        self.assertEqual(token, ADMIN_API_TOKEN_DEFAULT)
        self.assertEqual(token, "demo-admin-api-token-not-a-real-secret")
        self.assertNotIn("mcp-admin-9f8e7d6c5b4a3210", token)

    def test_environment_variables_override_defaults(self):
        override_env = {
            "DVMCP_CHALLENGE7_EMAIL_API_KEY": "runtime-email-api-key",
            "DVMCP_CHALLENGE7_STORAGE_ACCESS_TOKEN": "runtime-storage-access-token",
            "DVMCP_CHALLENGE7_ANALYTICS_REFRESH_TOKEN": "runtime-analytics-refresh-token",
            "DVMCP_CHALLENGE7_ADMIN_API_TOKEN": "runtime-admin-api-token",
        }
        with patch.dict(os.environ, override_env, clear=False):
            tokens = get_tokens()
            admin_token = get_admin_api_token()

        self.assertEqual(tokens["email_service"]["api_key"], "runtime-email-api-key")
        self.assertEqual(
            tokens["cloud_storage"]["access_token"], "runtime-storage-access-token"
        )
        self.assertEqual(
            tokens["analytics_platform"]["refresh_token"],
            "runtime-analytics-refresh-token",
        )
        self.assertEqual(admin_token, "runtime-admin-api-token")

    def test_all_three_services_have_full_token_fields(self):
        tokens = get_tokens()
        for service_id in ("email_service", "cloud_storage", "analytics_platform"):
            info = tokens[service_id]
            self.assertIn("service_name", info)
            self.assertIn("api_key", info)
            self.assertIn("access_token", info)
            self.assertIn("refresh_token", info)
            self.assertIn("expires_at", info)

    def test_no_real_secret_in_module_source(self):
        # Guard against regressions: the credential_store module itself must
        # not embed any of the reported live secrets.
        from challenges.medium.challenge7 import credential_store as cs

        with open(cs.__file__) as _f:
            source = _f.read()
        for secret in _REPORTED_LIVE_SECRETS:
            self.assertNotIn(
                secret, source, f"Live secret {secret!r} must not be in module source"
            )


if __name__ == "__main__":
    unittest.main()
