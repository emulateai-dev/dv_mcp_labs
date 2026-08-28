import os
import unittest
from unittest.mock import patch

from challenges.hard.challenge10 import secrets_store
from challenges.hard.challenge10.secrets_store import (
    get_system_conf,
    get_tokens,
    get_users,
    get_admin_dashboard,
)


class Challenge10SecretsStoreTests(unittest.TestCase):
    # The live secret values reported in the finding. None of these may
    # appear anywhere in the source-controlled defaults.
    REPORTED_LIVE_VALUES = [
        # system.conf secrets (server.py:28-37)
        "Pr0d-DB-S3cur3!P@$$w0rd",
        "apg-prod-8a7b6c5d4e3f2g1h",
        "9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g",
        "AKIAIOSFODNN7EXAMPLE",
        "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
        # JWT tokens (server.py:45-47)
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJhZG1pbiIsIm5hbWUiOiJBZG1pbiBVc2VyIiwicm9sZSI6ImFkbWluIiwiaWF0IjoxNjUxODg0ODAwfQ.8FhJ7Z5KFUEJFoQW2xeUL9_NOzlKB3j8fKvxU_5qB4Y",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJzZXJ2aWNlIiwibmFtZSI6IlNlcnZpY2UgQWNjb3VudCIsInJvbGUiOiJzZXJ2aWNlIiwiaWF0IjoxNjUxODg0ODAwfQ.7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g0f",
        "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJ1c2VyIiwibmFtZSI6IlJlZ3VsYXIgVXNlciIsInJvbGUiOiJ1c2VyIiwiaWF0IjoxNjUxODg0ODAwfQ.9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m",
        # user password hashes (server.py:58/64/70)
        "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        "b03ddf3ca2e714a6548e7495e2a03f5e824eaac9837cd7f159c67b905b4b7342",
        # cleartext password hints in comments
        "password: password",
        "password: service123",
        # master password (server.py:131)
        "m@st3r-p@$$w0rd-2025",
    ]

    def test_safe_defaults_do_not_ship_any_reported_live_secret(self):
        conf = get_system_conf()
        tokens = get_tokens()
        users = get_users()
        admin_dash = get_admin_dashboard()

        for live in self.REPORTED_LIVE_VALUES:
            self.assertNotIn(live, conf, f"live secret leaked into system.conf: {live!r}")
            self.assertNotIn(live, admin_dash, f"live secret leaked into admin dashboard: {live!r}")
            for tok in tokens.values():
                self.assertNotIn(live, tok, f"live secret leaked into a token: {live!r}")
            for u in users.values():
                self.assertNotIn(live, u["password_hash"], f"live hash leaked into users: {live!r}")

        # Safe placeholder defaults should be present instead.
        self.assertIn("demo-db-password-not-a-real-secret", conf)
        self.assertIn("demo-api-gateway-key-not-a-real-secret", conf)
        self.assertIn("demo-api-gateway-secret-not-a-real-secret", conf)
        self.assertIn("demo-aws-access-key-id-not-a-real-secret", conf)
        self.assertIn("demo-aws-secret-access-key-not-a-real-secret", conf)
        self.assertIn("demo-master-password-not-a-real-secret", admin_dash)
        self.assertEqual(tokens["admin_token"], "demo-admin-token-not-a-real-secret")

    def test_user_hashes_are_sha256_of_placeholder_passwords_not_live_values(self):
        import hashlib

        users = get_users()
        # The demo user hashes must be sha256 of the placeholder plaintexts,
        # i.e. NOT the originally-reported hashes.
        self.assertEqual(
            users["user"]["password_hash"],
            hashlib.sha256(b"demo-user-password").hexdigest(),
        )
        self.assertNotEqual(
            users["user"]["password_hash"],
            "5e884898da28047151d0e56f8dc6292773603d0d6aabbdd62a11ef721d1542d8",
        )

    def test_runtime_overrides_are_used_when_env_vars_set(self):
        env = {
            "DVMCP_CHALLENGE10_DB_PASSWORD": "runtime-db-secret",
            "DVMCP_CHALLENGE10_API_GATEWAY_KEY": "runtime-gw-key",
            "DVMCP_CHALLENGE10_API_GATEWAY_SECRET": "runtime-gw-secret",
            "DVMCP_CHALLENGE10_AWS_ACCESS_KEY_ID": "runtime-aws-id",
            "DVMCP_CHALLENGE10_AWS_SECRET_ACCESS_KEY": "runtime-aws-secret",
            "DVMCP_CHALLENGE10_ADMIN_TOKEN": "runtime-admin-token",
            "DVMCP_CHALLENGE10_SERVICE_TOKEN": "runtime-service-token",
            "DVMCP_CHALLENGE10_USER_TOKEN": "runtime-user-token",
            "DVMCP_CHALLENGE10_MASTER_PASSWORD": "runtime-master",
            "DVMCP_CHALLENGE10_ADMIN_PASSWORD": "runtime-admin-pw",
            "DVMCP_CHALLENGE10_SERVICE_PASSWORD": "runtime-service-pw",
            "DVMCP_CHALLENGE10_USER_PASSWORD": "runtime-user-pw",
        }
        with patch.dict(os.environ, env, clear=False):
            conf = get_system_conf()
            tokens = get_tokens()
            users = get_users()
            admin_dash = get_admin_dashboard()

        self.assertIn("runtime-db-secret", conf)
        self.assertIn("runtime-gw-key", conf)
        self.assertIn("runtime-gw-secret", conf)
        self.assertIn("runtime-aws-id", conf)
        self.assertIn("runtime-aws-secret", conf)
        self.assertEqual(tokens["admin_token"], "runtime-admin-token")
        self.assertEqual(tokens["service_token"], "runtime-service-token")
        self.assertEqual(tokens["user_token"], "runtime-user-token")
        self.assertIn("runtime-master", admin_dash)

        import hashlib
        self.assertEqual(
            users["admin"]["password_hash"],
            hashlib.sha256(b"runtime-admin-pw").hexdigest(),
        )

    def test_no_live_secret_string_lives_in_the_module_source(self):
        import inspect

        source = inspect.getsource(secrets_store)
        for live in self.REPORTED_LIVE_VALUES:
            self.assertNotIn(live, source, f"live secret hardcoded in module: {live!r}")


if __name__ == "__main__":
    unittest.main()
