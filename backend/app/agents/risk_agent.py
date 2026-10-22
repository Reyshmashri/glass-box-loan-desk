
def assess_transaction_risk(banking_result):
    """Assess simulated transactions using simple, explainable rules."""

    transactions_result = banking_result.get("transactions", {})
    transactions = transactions_result.get("transactions", [])

    if not isinstance(transactions, list):
        raise ValueError("Transaction data must be a list.")

    findings = []
    high_value_threshold = 10000

    for transaction in transactions:
        amount = transaction.get("amount", 0)
        transaction_id = transaction.get("transaction_id", "Unknown")

        if not isinstance(amount, (int, float)) or isinstance(amount, bool):
            raise ValueError(
                f"Invalid amount in transaction {transaction_id}."
            )

        if amount < 0:
            raise ValueError(
                f"Negative transaction amount in {transaction_id}."
            )

        if amount >= high_value_threshold:
            findings.append({
                "transaction_id": transaction_id,
                "rule": "HIGH_VALUE_TRANSACTION",
                "amount": amount,
                "reason": (
                    f"Transaction amount is at least "
                    f"₹{high_value_threshold}."
                ),
            })

    return {
        "risk_level": "Review" if findings else "No rule triggered",
        "findings": findings,
        "rules_checked": [
            {
                "rule": "HIGH_VALUE_TRANSACTION",
                "threshold_inr": high_value_threshold,
                "description": (
                    "Flags transactions of ₹10,000 or more for review."
                ),
            }
        ],
        "environment": "Simulated",
        "disclaimer": (
            "This is a demonstration rule, not a fraud determination. "
            "A flagged transaction is not necessarily fraudulent."
        ),
    }
