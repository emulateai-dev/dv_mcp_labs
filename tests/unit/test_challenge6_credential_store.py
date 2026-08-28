import os
import unittest
from unittest.mock import patch

from challenges.medium.challenge6.credential_store import (
    get_api_keys,
    get_internal_memo,
)


class Challenge6CredentialStoreTests(unittest.TestCase):
    # The live API-key values reported in the finding. None of these may
    # appear in the source-controlled defaults.
    REPORTED_LIVE_VALUES = [
        "api_prod_8a7b6c5d4e3f2g1h",
        "pg_live_9i8u7y6t5r4e3w2q",
        "as_prod_2p3o4i5u6y7t8r9e",
        "api_dev_1a2b3c4d5e6f7g8h",
        "pg_test_9i8u7y6t5r4e3w2q",
        "as_dev_2p3o4i5u6y7t8r9e",
    ]

    def test_safe_defaults_do_not_ship_the_reported_live_secret_values(self):
        memo = get_internal_memo()
        keys = get_api_keys()

        for live_value in self.REPORTED_LIVE_VALUES:
            self.assertNotIn(live_value, memo)
            self.assertNotIn(live_value, keys)

        # The safe placeholder defaults should be present instead.
        self.assertIn("demo-api-key-not-a-real-secret", keys)
        self.assertIn("demo-payment-gateway-key-not-a-real-secret", keys)
        self.assertIn("demo-analytics-key-not-a-real-secret", keys)
        self.assertIn("demo-dev-api-key-not-a-real-secret", keys)
        self.assertIn("demo-dev-payment-gateway-key-not-a-real-secret", keys)
        self.assertIn("demo-dev-analytics-key-not-a-real-secret", keys)

    def test_environment_variables_override_defaults(self):
        override_env = {
            "DVMCP_CHALLENGE6_MAIN_API_PROD": "runtime-main-api-prod",
            "DVMCP_CHALLENGE6_PAYMENT_GATEWAY_PROD": "runtime-pg-prod",
            "DVMCP_CHALLENGE6_ANALYTICS_SERVICE_PROD": "runtime-analytics-prod",
            "DVMCP_CHALLENGE6_MAIN_API_DEV": "runtime-main-api-dev",
            "DVMCP_CHALLENGE6_PAYMENT_GATEWAY_DEV": "runtime-pg-dev",
            "DVMCP_CHALLENGE6_ANALYTICS_SERVICE_DEV": "runtime-analytics-dev",
        }

        with patch.dict(os.environ, override_env, clear=False):
            memo = get_internal_memo()
            keys = get_api_keys()

        # Memo only carries the production keys.
        self.assertIn("Main API: runtime-main-api-prod", memo)
        self.assertIn("Payment Gateway: runtime-pg-prod", memo)
        self.assertIn("Analytics Service: runtime-analytics-prod", memo)

        # The credentials resource carries both prod and dev keys.
        self.assertIn("Main API: runtime-main-api-prod", keys)
        self.assertIn("Payment Gateway: runtime-pg-prod", keys)
        self.assertIn("Analytics Service: runtime-analytics-prod", keys)
        self.assertIn("Main API: runtime-main-api-dev", keys)
        self.assertIn("Payment Gateway: runtime-pg-dev", keys)
        self.assertIn("Analytics Service: runtime-analytics-dev", keys)


if __name__ == "__main__":
    unittest.main()
