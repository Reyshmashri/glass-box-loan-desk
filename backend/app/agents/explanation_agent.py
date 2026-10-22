def explain_decision(customer, finances, decision):
    return {
        "customerName": customer["name"],
        "decision": decision["decision"],
        "debtToIncomeRatio": finances["debt_to_income_ratio"],
        "reasons": decision["reasons"],
        "agent_steps": [
            "Customer Agent: validated applicant details",
            "Financial Agent: calculated financial ratios",
            "Loan Decision Agent: applied decision rules",
            "Explanation Agent: prepared the result",
        ],
        "environment": "Simulated",
        "disclaimer": (
            "Demonstration only. This is not a real lending decision."
        ),
    }