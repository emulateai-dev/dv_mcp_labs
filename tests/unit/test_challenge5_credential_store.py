import os
import unittest
from unittest.mock import patch

from challenges.medium.challenge5.credential_store import get_system_secrets


class Challenge5CredentialStoreTests(unittest.TestCase):
    def test_safe_defaults_do_not_ship_the_reported_live_secret_values(self):
        secrets = get_system_secrets()

        # The live values reported in the finding must NOT appear in source.
        self.assertNotIn("db_super_secret_password", secrets)
        self.assertNotIn("admin_password_2025", secrets)
        self.assertNotIn("dvmcp-lab-api-key-EXAMPLE", secrets)
        self.assertNotIn("4a5c8d9e2f1b3a7c6d5e4f3a2b1c0d9e8f", secrets)

        # The safe placeholder defaults should be present instead.
        self.assertIn("Database Password: demo-db-password-change-me", secrets)
        self.assertIn("Admin Account: demo_admin@example.com / demo-admin-password-change-me", secrets)
        self.assertIn("API Key: demo-api-key-not-a-real-secret", secrets)
        self.assertIn("Encryption Key: " + "0" * 32, secrets)

    def test_environment_variables_override_defaults(self):
        override_env = {
            "DVMCP_CHALLENGE5_DATABASE_PASSWORD": "runtime-db-password",
            "DVMCP_CHALLENGE5_ADMIN_USERNAME": "runtime_admin@example.com",
            "DVMCP_CHALLENGE5_ADMIN_PASSWORD": "runtime-admin-password",
            "DVMCP_CHALLENGE5_API_KEY": "runtime-api-key",
            "DVMCP_CHALLENGE5_ENCRYPTION_KEY": "a" * 32,
        }

        with patch.dict(os.environ, override_env, clear=False):
            secrets = get_system_secrets()

        self.assertIn("Database Password: runtime-db-password", secrets)
        self.assertIn("Admin Account: runtime_admin@example.com / runtime-admin-password", secrets)
        self.assertIn("API Key: runtime-api-key", secrets)
        self.assertIn("Encryption Key: " + "a" * 32, secrets)


if __name__ == "__main__":
    unittest.main()
