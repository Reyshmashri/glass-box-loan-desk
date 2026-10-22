def evaluate_decision(customer, finances):
    reasons = []

    if not 300 <= customer["credit_score"] <= 900:
        raise ValueError("Credit score must be between 300 and 900.")

    if customer["credit_score"] < 650:
        reasons.append("Credit score is below 650.")

    if finances["debt_to_income_ratio"] > 40:
        reasons.append("Monthly debt exceeds 40% of income.")

    if finances["loan_to_income_ratio"] > 10:
        reasons.append(
            "Requested loan exceeds 10 times monthly income."
        )

    return {
        "decision": (
            "Review Required" if reasons
            else "Eligible for Consideration"
        ),
        "reasons": reasons or [
            "The application meets the prototype's basic rules."
        ],
    }