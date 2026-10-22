import unittest

from app.agents.financial_agent import analyze_finances
from app.agents.credit_agent import evaluate_credit, find_counterfactuals
from app.agents.risk_agent import assess_transaction_risk
from app.agents.supervisor_agent import route_request


class TestFinancialAgent(unittest.TestCase):

    def _customer(self, income, debt, loan):
        return {
            "monthly_income": income,
            "monthly_debt": debt,
            "loan_amount": loan,
        }

    def test_ratios_calculated_correctly(self):
        f = analyze_finances(self._customer(50000, 10000, 200000))
        self.assertEqual(f["debt_to_income_ratio"], 20.0)
        self.assertEqual(f["loan_to_income_ratio"], 4.0)

    def test_zero_income_raises(self):
        with self.assertRaises(ValueError):
            analyze_finances(self._customer(0, 0, 100000))

    def test_negative_loan_raises(self):
        with self.assertRaises(ValueError):
            analyze_finances(self._customer(50000, 0, -1))


class TestCreditAgent(unittest.TestCase):

    def _run(self, credit_score, debt_ratio, loan_ratio):
        customer = {"credit_score": credit_score}
        finances = {
            "debt_to_income_ratio": debt_ratio,
            "loan_to_income_ratio": loan_ratio,
        }
        return evaluate_credit(customer, finances)

    def test_all_rules_pass(self):
        r = self._run(700, 30, 5)
        self.assertEqual(r["decision"], "Eligible for Consideration")
        self.assertTrue(all(rule["passed"] for rule in r["rules_checked"]))

    def test_low_credit_score_fails(self):
        r = self._run(600, 30, 5)
        self.assertEqual(r["decision"], "Review Required")
        failed = [rule for rule in r["rules_checked"] if not rule["passed"]]
        self.assertTrue(
            any(rule["rule"] == "MINIMUM_CREDIT_SCORE" for rule in failed)
        )

    def test_high_debt_ratio_fails(self):
        r = self._run(700, 50, 5)
        self.assertEqual(r["decision"], "Review Required")

    def test_high_loan_ratio_fails(self):
        r = self._run(700, 30, 15)
        self.assertEqual(r["decision"], "Review Required")

    def test_invalid_credit_score_raises(self):
        with self.assertRaises(ValueError):
            self._run(200, 30, 5)

    def test_counterfactuals_suggests_credit_score(self):
        customer = {"credit_score": 600}
        finances = {"debt_to_income_ratio": 30, "loan_to_income_ratio": 5}
        r = find_counterfactuals(customer, finances)
        factors = [s["factor"] for s in r["suggestions"]]
        self.assertIn("credit_score", factors)

    def test_counterfactuals_empty_when_eligible(self):
        customer = {"credit_score": 700}
        finances = {"debt_to_income_ratio": 30, "loan_to_income_ratio": 5}
        r = find_counterfactuals(customer, finances)
        self.assertEqual(r["suggestions"], [])


class TestRiskAgent(unittest.TestCase):

    def _banking_result(self, transactions):
        return {"transactions": {"transactions": transactions}}

    def test_high_value_transaction_flagged(self):
        txns = [{"transaction_id": "T-001", "amount": 15000.0}]
        r = assess_transaction_risk(self._banking_result(txns))
        self.assertEqual(r["risk_level"], "Review")
        self.assertEqual(len(r["findings"]), 1)

    def test_low_value_transaction_not_flagged(self):
        txns = [{"transaction_id": "T-002", "amount": 500.0}]
        r = assess_transaction_risk(self._banking_result(txns))
        self.assertEqual(r["risk_level"], "No rule triggered")
        self.assertEqual(r["findings"], [])

    def test_empty_transactions(self):
        r = assess_transaction_risk(self._banking_result([]))
        self.assertEqual(r["risk_level"], "No rule triggered")


class TestSupervisorAgent(unittest.TestCase):

    def test_known_workflows_return_no_clarification(self):
        for wf in ("account_lookup", "suspicious_txn", "loan_check", "what_if"):
            r = route_request(wf)
            self.assertFalse(r["needs_clarification"])
            self.assertIn("agents", r)

    def test_unknown_workflow_needs_clarification(self):
        r = route_request("book_flight")
        self.assertTrue(r["needs_clarification"])

    def test_non_string_raises(self):
        with self.assertRaises(ValueError):
            route_request(None)


if __name__ == "__main__":
    unittest.main()
