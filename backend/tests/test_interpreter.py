import json
import unittest
from unittest.mock import MagicMock, patch

from app.agents.gemini_interpreter import interpret_request_locally, _parse_and_validate


# ---------------------------------------------------------------------------
# Local fallback tests (unchanged)
# ---------------------------------------------------------------------------

class TestLocalInterpreter(unittest.TestCase):

    def test_loan_check_full(self):
        r = interpret_request_locally(
            "Check if CUST-1001 qualifies for a loan of 200000"
        )
        self.assertEqual(r["request_type"], "loan_check")
        self.assertEqual(r["customer_id"], "CUST-1001")
        self.assertEqual(r["loan_amount"], 200000.0)
        self.assertFalse(r["needs_clarification"])

    def test_what_if(self):
        r = interpret_request_locally(
            "What if CUST-1002 wanted to improve eligibility for 300000"
        )
        self.assertEqual(r["request_type"], "what_if")
        self.assertEqual(r["customer_id"], "CUST-1002")

    def test_account_lookup(self):
        r = interpret_request_locally("Show account details for CUST-1003")
        self.assertEqual(r["request_type"], "account_lookup")
        self.assertEqual(r["customer_id"], "CUST-1003")
        self.assertFalse(r["needs_clarification"])

    def test_suspicious_txn(self):
        r = interpret_request_locally(
            "Review suspicious transactions for CUST-1001"
        )
        self.assertEqual(r["request_type"], "suspicious_txn")
        self.assertEqual(r["customer_id"], "CUST-1001")

    def test_missing_customer_id_asks_clarification(self):
        r = interpret_request_locally("Check loan eligibility for 150000")
        self.assertTrue(r["needs_clarification"])
        self.assertIsNotNone(r["clarification"])

    def test_missing_loan_amount_asks_clarification(self):
        r = interpret_request_locally("Loan check for CUST-1001")
        self.assertTrue(r["needs_clarification"])

    def test_unknown_request(self):
        r = interpret_request_locally("Book me a flight to Mumbai")
        self.assertEqual(r["request_type"], "unknown")
        self.assertTrue(r["needs_clarification"])

    def test_empty_message_raises(self):
        with self.assertRaises(ValueError):
            interpret_request_locally("")

    def test_case_insensitive_customer_id(self):
        r = interpret_request_locally("account lookup for cust-1002")
        self.assertEqual(r["customer_id"], "CUST-1002")

    def test_loan_amount_with_commas(self):
        r = interpret_request_locally(
            "Loan check for CUST-1003 for 2,50,000"
        )
        self.assertEqual(r["loan_amount"], 250000.0)

    def test_loan_amount_plain(self):
        r = interpret_request_locally("Can CUST-1001 get a loan of 200000")
        self.assertEqual(r["loan_amount"], 200000.0)
        self.assertFalse(r["needs_clarification"])

    def test_loan_amount_rupee_symbol_with_commas(self):
        r = interpret_request_locally("Loan check for CUST-1002 for ₹2,00,000")
        self.assertEqual(r["loan_amount"], 200000.0)
        self.assertFalse(r["needs_clarification"])

    def test_loan_amount_lakh_notation(self):
        r = interpret_request_locally("Can CUST-1003 borrow 2 lakh")
        self.assertEqual(r["loan_amount"], 200000.0)
        self.assertFalse(r["needs_clarification"])

    def test_customer_id_digits_not_parsed_as_loan_amount(self):
        r = interpret_request_locally("account lookup for CUST-1003")
        self.assertIsNone(r["loan_amount"])


# ---------------------------------------------------------------------------
# Mocked Gemini interpret_banking_request tests
# ---------------------------------------------------------------------------

def _make_gemini_response(content: str):
    """Build a minimal mock that looks like a Gemini response."""
    mock_response = MagicMock()
    mock_response.text = content
    return mock_response


def _json(request_type, customer_id, loan_amount, needs_clarification=False, clarification=None):
    return json.dumps({
        "request_type": request_type,
        "customer_id": customer_id,
        "loan_amount": loan_amount,
        "needs_clarification": needs_clarification,
        "clarification": clarification,
    })


class TestInterpretBankingRequestGemini(unittest.TestCase):
    """Tests for interpret_banking_request using a mocked Gemini client."""

    def _call(self, model_response: str):
        from app.agents.gemini_interpreter import interpret_banking_request

        mock_client = MagicMock()
        mock_client.models.generate_content.return_value = _make_gemini_response(
            model_response
        )

        with patch.dict("os.environ", {"GEMINI_API_KEY": "AIza-test-key"}):
            with patch("app.agents.gemini_interpreter.genai.Client", return_value=mock_client):
                return interpret_banking_request("dummy message")

    def test_loan_check_valid_response(self):
        r = self._call(_json("loan_check", "CUST-1001", 200000))
        self.assertEqual(r["request_type"], "loan_check")
        self.assertEqual(r["customer_id"], "CUST-1001")
        self.assertEqual(r["loan_amount"], 200000)
        self.assertFalse(r["needs_clarification"])

    def test_account_lookup_valid_response(self):
        r = self._call(_json("account_lookup", "CUST-1002", None))
        self.assertEqual(r["request_type"], "account_lookup")
        self.assertEqual(r["customer_id"], "CUST-1002")

    def test_suspicious_txn_valid_response(self):
        r = self._call(_json("suspicious_txn", "CUST-1003", None))
        self.assertEqual(r["request_type"], "suspicious_txn")

    def test_what_if_valid_response(self):
        r = self._call(_json("what_if", "CUST-1003", 300000))
        self.assertEqual(r["request_type"], "what_if")
        self.assertEqual(r["loan_amount"], 300000)

    def test_missing_api_key_raises(self):
        from app.agents.gemini_interpreter import interpret_banking_request
        import os
        with patch.dict("os.environ", {}, clear=True):
            os.environ.pop("GEMINI_API_KEY", None)
            with self.assertRaises(RuntimeError) as ctx:
                interpret_banking_request("any message")
        self.assertIn("GEMINI_API_KEY", str(ctx.exception))

    def test_api_error_raises_runtime_error(self):
        from app.agents.gemini_interpreter import interpret_banking_request

        mock_client = MagicMock()
        mock_client.models.generate_content.side_effect = Exception("network error")

        with patch.dict("os.environ", {"GEMINI_API_KEY": "AIza-test-key"}):
            with patch("app.agents.gemini_interpreter.genai.Client", return_value=mock_client):
                with self.assertRaises(RuntimeError):
                    interpret_banking_request("any message")

    def test_invalid_json_raises_runtime_error(self):
        with self.assertRaises(RuntimeError):
            self._call("not json at all")

    def test_unsupported_workflow_raises(self):
        with self.assertRaises(RuntimeError):
            self._call(_json("book_flight", None, None))

    def test_model_wrapped_in_markdown_fence(self):
        inner = _json("account_lookup", "CUST-1001", None)
        r = self._call(f"```json\n{inner}\n```")
        self.assertEqual(r["request_type"], "account_lookup")


# ---------------------------------------------------------------------------
# _parse_and_validate unit tests
# ---------------------------------------------------------------------------

class TestParseAndValidate(unittest.TestCase):

    def _valid(self, **kwargs):
        return json.dumps({
            "request_type": "account_lookup",
            "customer_id": "CUST-1001",
            "loan_amount": None,
            "needs_clarification": False,
            "clarification": None,
            **kwargs,
        })

    def test_valid_account_lookup(self):
        r = _parse_and_validate(self._valid())
        self.assertEqual(r["request_type"], "account_lookup")
        self.assertEqual(r["customer_id"], "CUST-1001")

    def test_invalid_customer_id_raises(self):
        with self.assertRaises(RuntimeError):
            _parse_and_validate(self._valid(customer_id="CUST-9999"))

    def test_no_json_raises(self):
        with self.assertRaises(RuntimeError):
            _parse_and_validate("no braces here")

    def test_loan_check_missing_amount_sets_clarification(self):
        r = _parse_and_validate(self._valid(request_type="loan_check", loan_amount=None))
        self.assertTrue(r["needs_clarification"])

    def test_negative_loan_amount_raises(self):
        with self.assertRaises(RuntimeError):
            _parse_and_validate(self._valid(request_type="loan_check", loan_amount=-500))


if __name__ == "__main__":
    unittest.main()
