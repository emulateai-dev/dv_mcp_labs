import unittest

from challenges.hard.challenge10.credential_store import (
    get_credentials,
    get_system_conf,
)


class Challenge10CredentialStoreTests(unittest.TestCase):
    # The live secret values reported in the finding. None of these may
    # appear in the source-controlled defaults.
    REPORTED_LIVE_VALUES = [
        "Pr0d-DB-S3cur3!P@$$w0rd",
        "apg-prod-8a7b6c5d4e3f2g1h",
        "9i8u7y6t5r4e3w2q1z0x9c8v7b6n5m4k3j2h1g",
        "AKIAIOSFODNN7EXAMPLE",
        "wJalrXUtnFEMI/K7MDENG/bPxRfiCYEXAMPLEKEY",
    ]

    def test_safe_defaults_do_not_ship_the_reported_live_secret_values(self):
        creds = get_credentials()
        conf = get_system_conf()

        for live_value in self.REPORTED_LIVE_VALUES:
            self.assertNotIn(live_value, conf)
            for v in creds.values():
                self.assertNotIn(live_value, v)

        # The safe placeholder defaults should be present instead.
        self.assertIn("demo-db-password-not-a-real-secret", conf)
        self.assertIn("demo-api-gateway-key-not-a-real-secret", conf)
        self.assertIn("demo-api-gateway-secret-not-a-real-secret", conf)
        self.assertIn("demo-aws-access-key-id-not-a-real-secret", conf)
        self.assertIn("demo-aws-secret-access-key-not-a-real-secret", conf)

    def test_runtime_override_is_used_when_env_var_set(self):
        import os
        from unittest.mock import patch

        env = {
            "DVMCP_CHALLENGE10_DB_PASSWORD": "runtime-db-secret",
            "DVMCP_CHALLENGE10_API_GATEWAY_KEY": "runtime-gw-key",
            "DVMCP_CHALLENGE10_API_GATEWAY_SECRET": "runtime-gw-secret",
            "DVMCP_CHALLENGE10_AWS_ACCESS_KEY_ID": "runtime-aws-id",
            "DVMCP_CHALLENGE10_AWS_SECRET_ACCESS_KEY": "runtime-aws-secret",
        }
        with patch.dict(os.environ, env, clear=False):
            conf = get_system_conf()
        self.assertIn("runtime-db-secret", conf)
        self.assertIn("runtime-gw-key", conf)
        self.assertIn("runtime-gw-secret", conf)
        self.assertIn("runtime-aws-id", conf)
        self.assertIn("runtime-aws-secret", conf)


if __name__ == "__main__":
    unittest.main()
