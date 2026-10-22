
def route_request(request_type: str) -> dict:
    """Choose the agents required for a supported banking request."""

    if not isinstance(request_type, str):
        raise ValueError("Request type must be a string.")

    request_type = request_type.strip().lower()

    routes = {
        "account_lookup": {
            "agents": ["Banking Agent"],
            "description": "Retrieve customer account information.",
        },
        "suspicious_txn": {
            "agents": ["Banking Agent", "Risk Agent"],
            "description": (
                "Review transactions and assess account risk."
            ),
        },
        "loan_check": {
            "agents": [
                "Banking Agent",
                "Financial Agent",
                "Credit Agent",
            ],
            "description": (
                "Retrieve customer information, analyze finances, "
                "and evaluate loan eligibility."
            ),
        },
        "what_if": {
            "agents": [
                "Banking Agent",
                "Financial Agent",
                "Credit Agent",
            ],
            "description": (
                "Analyze customer finances and suggest changes "
                "that could improve loan eligibility."
            ),
        },
    }

    if request_type not in routes:
        return {
            "request_type": request_type,
            "agents": [],
            "description": (
                "Request type is unknown. Ask the user for clarification."
            ),
            "needs_clarification": True,
        }

    return {
        "request_type": request_type,
        **routes[request_type],
        "needs_clarification": False,
    }
