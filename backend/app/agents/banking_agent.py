
from app.tools.customer_tools import (
    get_customer_profile,
    get_account_balance,
    get_transactions,
    assess_account_health,
)


def handle_banking_request(request_type, customer_id):
    """Execute a supported banking request using simulated data."""

    if not isinstance(customer_id, str) or not customer_id.strip():
        raise ValueError("Customer ID is required.")

    if request_type == "account_lookup":
        return {
            "customer": get_customer_profile(customer_id),
            "account": get_account_balance(customer_id),
        }

    if request_type == "suspicious_txn":
        return {
            "customer": get_customer_profile(customer_id),
            "transactions": get_transactions(customer_id, limit=5),
            "account_health": assess_account_health(customer_id),
        }

    raise ValueError(
        f"Unsupported banking request type: {request_type}"
    )
