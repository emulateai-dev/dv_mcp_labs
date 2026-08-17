import json
import os
import tempfile
import unittest
from unittest.mock import patch

from challenges.medium.challenge7.token_store import (
    get_tokens,
    write_tokens,
)


# The live values reported by the finding must never be shipped in source.
_REPORTED_LIVE_SECRETS = [
    "epro_api_5f4e3d2c1b0a9z8y7x",
    "cbx_api_1a2b3c4d5e6f7g8h9i",
    "dm_api_9z8y7x6w5v4u3t2s1r",
    "rt_7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g0f",
    "rt_9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m",
    "rt_3e4r5t6y7u8i9o0p1a2s3d4f5g6h7j",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxMjM0NTY3ODkwIiwibmFtZSI6IkFDTUUgQ29ycCIsImVtYWlsX2FjY2VzcyI6InRydWUiLCJpYXQiOjE2NTE4ODQ4MDB9.5TxfEAVbZRGbKnXaL9Lrx9NqXSNFw2ac4FDzPHvRzSQ",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI5ODc2NTQzMjEwIiwibmFtZSI6IkFDTUUgQ29ycCIsInN0b3JhZ2VfYWNjZXNzIjoidHJ1ZSIsImlhdCI6MTY1MTg4NDgwMH0.8FhJ7Z5KFUEJFoQW2xeUL9_NOzlKB3j8fKvxU_5qB4Y",
    "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiI1NDMyMTA5ODc2IiwibmFtZSI6IkFDTUUgQ29ycCIsImFuYWx5dGljc19hY2Nlc3MiOiJ0cnVlIiwiaWF0IjoxNjUxODg0ODAwfQ.QzHJ2_8NXiPd5Vl6r3S1VJqFaC3-U_a9FPRJXBgU8Pg",
]


class Challenge7TokenStoreTests(unittest.TestCase):
    def test_safe_defaults_do_not_ship_the_reported_live_secrets(self):
        tokens = get_tokens()
        rendered = json.dumps(tokens)
        for secret in _REPORTED_LIVE_SECRETS:
            self.assertNotIn(secret, rendered, f"live secret leaked into defaults: {secret}")

    def test_safe_defaults_use_placeholder_values(self):
        tokens = get_tokens()
        self.assertEqual(tokens["email_service"]["api_key"], "demo-email-api-key-not-a-real-secret")
        self.assertEqual(
            tokens["cloud_storage"]["access_token"],
            "demo-cloud-storage-access-token-not-a-real-secret",
        )
        self.assertEqual(
            tokens["analytics_platform"]["refresh_token"],
            "demo-analytics-refresh-token-not-a-real-secret",
        )
        # Non-secret metadata is preserved.
        self.assertEqual(tokens["email_service"]["service_name"], "EmailPro API")
        self.assertEqual(tokens["email_service"]["expires_at"], "2025-12-31T23:59:59Z")

    def test_environment_variables_override_defaults(self):
        override_env = {
            "DVMCP_CHALLENGE7_EMAIL_API_KEY": "runtime-email-api-key",
            "DVMCP_CHALLENGE7_EMAIL_ACCESS_TOKEN": "runtime-email-access-token",
            "DVMCP_CHALLENGE7_EMAIL_REFRESH_TOKEN": "runtime-email-refresh-token",
            "DVMCP_CHALLENGE7_CLOUD_STORAGE_API_KEY": "runtime-cloud-api-key",
            "DVMCP_CHALLENGE7_CLOUD_STORAGE_ACCESS_TOKEN": "runtime-cloud-access-token",
            "DVMCP_CHALLENGE7_CLOUD_STORAGE_REFRESH_TOKEN": "runtime-cloud-refresh-token",
            "DVMCP_CHALLENGE7_ANALYTICS_API_KEY": "runtime-analytics-api-key",
            "DVMCP_CHALLENGE7_ANALYTICS_ACCESS_TOKEN": "runtime-analytics-access-token",
            "DVMCP_CHALLENGE7_ANALYTICS_REFRESH_TOKEN": "runtime-analytics-refresh-token",
        }
        with patch.dict(os.environ, override_env, clear=False):
            tokens = get_tokens()

        self.assertEqual(tokens["email_service"]["api_key"], "runtime-email-api-key")
        self.assertEqual(tokens["email_service"]["access_token"], "runtime-email-access-token")
        self.assertEqual(tokens["email_service"]["refresh_token"], "runtime-email-refresh-token")
        self.assertEqual(tokens["cloud_storage"]["api_key"], "runtime-cloud-api-key")
        self.assertEqual(tokens["analytics_platform"]["access_token"], "runtime-analytics-access-token")
        self.assertEqual(tokens["analytics_platform"]["refresh_token"], "runtime-analytics-refresh-token")
        # Static metadata is unaffected by env overrides.
        self.assertEqual(tokens["cloud_storage"]["service_name"], "CloudBox Storage")

    def test_write_tokens_materializes_file_with_safe_defaults(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = os.path.join(tmp, "nested", "tokens.json")
            content = write_tokens(path)
            self.assertTrue(os.path.exists(path))
            with open(path) as _f:
                on_disk = _f.read()
            self.assertEqual(json.loads(on_disk), json.loads(content))

            for secret in _REPORTED_LIVE_SECRETS:
                self.assertNotIn(secret, on_disk, f"live secret written to disk: {secret}")

            data = json.loads(on_disk)
            self.assertEqual(data["email_service"]["api_key"], "demo-email-api-key-not-a-real-secret")
            self.assertEqual(data["analytics_platform"]["service_name"], "DataMetrics Analytics")


if __name__ == "__main__":
    unittest.main()
