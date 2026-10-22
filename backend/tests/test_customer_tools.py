
import unittest

from app.tools.customer_tools import (
    get_customer_profile,
    get_account_balance,
    get_transactions,
)


class TestCustomerProfile(unittest.TestCase):

    def test_valid_customer(self):
        customer = get_customer_profile("CUST-1001")
        self.assertEqual(customer["customer_id"], "CUST-1001")
        self.assertEqual(customer["monthly_income"], 65000)

    def test_customer_id_is_case_insensitive(self):
        customer = get_customer_profile("cust-1001")
        self.assertEqual(customer["customer_id"], "CUST-1001")

    def test_invalid_customer(self):
        with self.assertRaises(ValueError):
            get_customer_profile("CUST-9999")

    def test_missing_customer_id(self):
        with self.assertRaises(ValueError):
            get_customer_profile("")

    
    def test_valid_account_balance(self):
        result = get_account_balance("CUST-1001")
        self.assertEqual(result["account_id"], "ACC-2001")
        self.assertEqual(result["balance"], 125000.00)
        self.assertEqual(result["currency"], "INR")

    def test_invalid_customer_balance(self):
        with self.assertRaises(ValueError):
            get_account_balance("CUST-9999")

    
    def test_get_recent_transactions(self):
        result = get_transactions("CUST-1001", 3)
        self.assertEqual(len(result["transactions"]), 3)
        self.assertEqual(result["count"], 3)
        self.assertEqual(result["transactions"][0]["transaction_id"], "T-1042")

    def test_invalid_transaction_limit(self):
        with self.assertRaises(ValueError):
            get_transactions("CUST-1001", 0)

    def test_invalid_customer_transactions(self):
        with self.assertRaises(ValueError):
            get_transactions("CUST-9999", 5)

   
if __name__ == "__main__":
    unittest.main()
