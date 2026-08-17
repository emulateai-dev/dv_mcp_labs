import os
import unittest
from unittest.mock import patch

from challenges.medium.challenge6.credential_store import (
    get_internal_memo,
    get_api_keys,
)


class Challenge6CredentialStoreTests(unittest.TestCase):
    def test_safe_defaults_do_not_ship_the_reported_live_secret_values(self):
        memo = get_internal_memo()
        self.assertIn("Main API: demo-api-key-not-a-real-secret", memo)
        self.assertIn("Payment Gateway: demo-payment-gateway-key-not-a-real-secret", memo)
        self.assertIn("Analytics Service: demo-analytics-key-not-a-real-secret", memo)

        # The live values reported by the finding must never appear in the defaults.
        self.assertNotIn("api_prod_8a7b6c5d4e3f2g1h", memo)
        self.assertNotIn("pg_live_9i8u7y6t5r4e3w2q", memo)
        self.assertNotIn("as_prod_2p3o4i5u6y7t8r9e", memo)

    def test_safe_defaults_do_not_ship_live_dev_secret_values(self):
        keys = get_api_keys()
        self.assertIn("Main API: demo-api-key-not-a-real-secret", keys)
        self.assertIn("Main API: demo-dev-api-key-not-a-real-secret", keys)
        self.assertNotIn("api_dev_1a2b3c4d5e6f7g8h", keys)
        self.assertNotIn("pg_test_9i8u7y6t5r4e3w2q", keys)
        self.assertNotIn("as_dev_2p3o4i5u6y7t8r9e", keys)

    def test_environment_variables_override_defaults(self):
        override_env = {
            "DVMCP_CHALLENGE6_MAIN_API_PROD": "runtime-prod-main-api",
            "DVMCP_CHALLENGE6_PAYMENT_GATEWAY_PROD": "runtime-prod-payment-gateway",
            "DVMCP_CHALLENGE6_ANALYTICS_SERVICE_PROD": "runtime-prod-analytics",
            "DVMCP_CHALLENGE6_MAIN_API_DEV": "runtime-dev-main-api",
            "DVMCP_CHALLENGE6_PAYMENT_GATEWAY_DEV": "runtime-dev-payment-gateway",
            "DVMCP_CHALLENGE6_ANALYTICS_SERVICE_DEV": "runtime-dev-analytics",
        }

        with patch.dict(os.environ, override_env, clear=False):
            memo = get_internal_memo()
            keys = get_api_keys()

        self.assertIn("Main API: runtime-prod-main-api", memo)
        self.assertIn("Payment Gateway: runtime-prod-payment-gateway", memo)
        self.assertIn("Analytics Service: runtime-prod-analytics", memo)

        self.assertIn("Main API: runtime-prod-main-api", keys)
        self.assertIn("Main API: runtime-dev-main-api", keys)
        self.assertIn("Payment Gateway: runtime-prod-payment-gateway", keys)
        self.assertIn("Analytics Service: runtime-dev-analytics", keys)


if __name__ == "__main__":
    unittest.main()
