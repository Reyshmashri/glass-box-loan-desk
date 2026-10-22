import unittest

import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), ".."))

from server import app


class TestRouteRequest(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def post(self, payload):
        return self.client.post(
            "/route-request",
            json=payload,
            content_type="application/json",
        )

    def test_account_lookup(self):
        r = self.post({"request_type": "account_lookup", "customer_id": "CUST-1001"})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("banking_result", data)
        self.assertIn("agent_trace", data)

    def test_suspicious_txn(self):
        r = self.post({"request_type": "suspicious_txn", "customer_id": "CUST-1002"})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("risk_result", data)

    def test_loan_check(self):
        r = self.post({
            "request_type": "loan_check",
            "customer_id": "CUST-1001",
            "loan_amount": 200000,
        })
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("credit_result", data)
        self.assertIn("financial_analysis", data)

    def test_what_if(self):
        r = self.post({
            "request_type": "what_if",
            "customer_id": "CUST-1003",
            "loan_amount": 500000,
        })
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("what_if_result", data)

    def test_unknown_workflow_returns_clarification(self):
        r = self.post({"request_type": "unknown_xyz"})
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertTrue(data["needs_clarification"])

    def test_missing_customer_id_returns_400(self):
        r = self.post({"request_type": "loan_check", "loan_amount": 100000})
        self.assertEqual(r.status_code, 400)

    def test_missing_loan_amount_returns_400(self):
        r = self.post({"request_type": "loan_check", "customer_id": "CUST-1001"})
        self.assertEqual(r.status_code, 400)

    def test_invalid_customer_id_returns_400(self):
        r = self.post({
            "request_type": "account_lookup",
            "customer_id": "CUST-9999",
        })
        self.assertEqual(r.status_code, 400)


class TestInterpretEndpoint(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def post(self, message):
        return self.client.post(
            "/interpret",
            json={"message": message},
            content_type="application/json",
        )

    def test_loan_check_end_to_end(self):
        r = self.post("Check loan eligibility for CUST-1001 for 200000")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("interpreted_as", data)
        self.assertIn("credit_result", data)

    def test_account_lookup_end_to_end(self):
        r = self.post("Show account details for CUST-1002")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("banking_result", data)

    def test_suspicious_txn_end_to_end(self):
        r = self.post("Review suspicious transactions for CUST-1003")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("risk_result", data)

    def test_what_if_end_to_end(self):
        r = self.post(
            "What if CUST-1003 wanted to improve eligibility for 300000"
        )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertIn("what_if_result", data)

    def test_missing_info_returns_clarification(self):
        r = self.post("Check loan eligibility")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertTrue(data["needs_clarification"])

    def test_unknown_request_returns_clarification(self):
        r = self.post("Book me a flight to Delhi")
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertTrue(data["needs_clarification"])

    def test_empty_message_returns_400(self):
        r = self.post("")
        self.assertEqual(r.status_code, 400)


class TestEvaluateLoan(unittest.TestCase):

    def setUp(self):
        app.testing = True
        self.client = app.test_client()

    def _valid_payload(self, **overrides):
        payload = {
            "name": "Test User",
            "monthlyIncome": 50000,
            "loanAmount": 200000,
            "monthlyDebt": 5000,
            "employmentType": "Salaried",
            "creditScore": 720,
        }
        payload.update(overrides)
        return payload

    def test_eligible_application(self):
        r = self.client.post("/evaluate-loan", json=self._valid_payload())
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["decision"], "Eligible for Consideration")
        self.assertIn("agent_trace", data)

    def test_review_required_low_credit(self):
        r = self.client.post(
            "/evaluate-loan", json=self._valid_payload(creditScore=600)
        )
        self.assertEqual(r.status_code, 200)
        data = r.get_json()
        self.assertEqual(data["decision"], "Review Required")

    def test_missing_name_returns_400(self):
        r = self.client.post(
            "/evaluate-loan", json=self._valid_payload(name="")
        )
        self.assertEqual(r.status_code, 400)

    def test_invalid_credit_score_returns_400(self):
        r = self.client.post(
            "/evaluate-loan", json=self._valid_payload(creditScore=100)
        )
        self.assertEqual(r.status_code, 400)


if __name__ == "__main__":
    unittest.main()
