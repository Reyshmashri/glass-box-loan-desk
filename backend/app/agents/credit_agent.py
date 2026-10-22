
def evaluate_credit(customer, finances):
    credit_score = customer.get("credit_score")
    debt_ratio = finances.get("debt_to_income_ratio")
    loan_ratio = finances.get("loan_to_income_ratio")

    if (
        not isinstance(credit_score, (int, float))
        or isinstance(credit_score, bool)
        or not 300 <= credit_score <= 900
    ):
        raise ValueError("Credit score must be between 300 and 900.")

    if (
        not isinstance(debt_ratio, (int, float))
        or isinstance(debt_ratio, bool)
        or debt_ratio < 0
    ):
        raise ValueError("Debt-to-income ratio must be a non-negative number.")

    if (
        not isinstance(loan_ratio, (int, float))
        or isinstance(loan_ratio, bool)
        or loan_ratio < 0
    ):
        raise ValueError("Loan-to-income ratio must be a non-negative number.")

    rules_checked = [
        {
            "rule": "MINIMUM_CREDIT_SCORE",
            "threshold": 650,
            "passed": credit_score >= 650,
            "reason": "Credit score must be at least 650.",
        },
        {
            "rule": "MAXIMUM_DEBT_TO_INCOME",
            "threshold_percent": 40,
            "passed": debt_ratio <= 40,
            "reason": "Monthly debt must not exceed 40% of income.",
        },
        {
            "rule": "MAXIMUM_LOAN_TO_MONTHLY_INCOME",
            "threshold": 10,
            "passed": loan_ratio <= 10,
            "reason": "Requested loan must not exceed 10 times monthly income.",
        },
    ]

    failed_rules = [rule for rule in rules_checked if not rule["passed"]]

    return {
        "decision": (
            "Review Required" if failed_rules else "Eligible for Consideration"
        ),
        "rules_checked": rules_checked,
        "reasons": (
            [rule["reason"] for rule in failed_rules]
            if failed_rules
            else ["The application meets the prototype's basic rules."]
        ),
        "environment": "Simulated",
        "disclaimer": "Demonstration only. This is not a real lending decision.",
    }


def find_counterfactuals(customer, finances):
    result = evaluate_credit(customer, finances)
    suggestions = []

    credit_score = customer["credit_score"]
    debt_ratio = finances["debt_to_income_ratio"]
    loan_ratio = finances["loan_to_income_ratio"]

    if credit_score < 650:
        suggestions.append({
            "factor": "credit_score",
            "current_value": credit_score,
            "target_value": 650,
            "suggestion": "A credit score of at least 650 would satisfy this rule.",
        })

    if debt_ratio > 40:
        suggestions.append({
            "factor": "debt_to_income_ratio",
            "current_value": debt_ratio,
            "target_value": 40,
            "suggestion": "Reduce monthly debt to 40% or less of monthly income.",
        })

    if loan_ratio > 10:
        suggestions.append({
            "factor": "loan_to_monthly_income",
            "current_value": loan_ratio,
            "target_value": 10,
            "suggestion": "Reduce the requested loan to 10 times monthly income or less.",
        })

    return {
        "current_decision": result["decision"],
        "suggestions": suggestions,
        "note": (
            "These are hypothetical rule-based suggestions. "
            "Meeting them does not guarantee loan approval."
        ),
        "environment": "Simulated",
    }
