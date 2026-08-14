import os
import unittest
from unittest.mock import patch

from challenges.easy.challenge1.credential_store import get_internal_credentials


class Challenge1CredentialStoreTests(unittest.TestCase):
    def test_safe_defaults_do_not_ship_the_reported_live_secret_values(self):
        credentials = get_internal_credentials()

        self.assertIn("Admin Username: demo_admin_user", credentials)
        self.assertIn("Admin Password: demo-password-change-me", credentials)
        self.assertIn("API Key: demo-api-key-not-a-real-secret", credentials)
        self.assertIn(
            "Database Connection String: postgresql://demo_user:demo_password@localhost/demo_challenge1",
            credentials,
        )

    def test_environment_variables_override_defaults(self):
        override_env = {
            "DVMCP_CHALLENGE1_ADMIN_USERNAME": "runtime_admin",
            "DVMCP_CHALLENGE1_ADMIN_PASSWORD": "runtime-password",
            "DVMCP_CHALLENGE1_API_KEY": "runtime-api-key",
            "DVMCP_CHALLENGE1_DATABASE_URL": "postgresql://runtime_user:runtime_pass@db/runtime",
        }

        with patch.dict(os.environ, override_env, clear=False):
            credentials = get_internal_credentials()

        self.assertIn("Admin Username: runtime_admin", credentials)
        self.assertIn("Admin Password: runtime-password", credentials)
        self.assertIn("API Key: runtime-api-key", credentials)
        self.assertIn(
            "Database Connection String: postgresql://runtime_user:runtime_pass@db/runtime",
            credentials,
        )


if __name__ == "__main__":
    unittest.main()
