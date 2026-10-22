
from app.data.mock_data import CUSTOMERS, ACCOUNT_BALANCES, TRANSACTIONS


def get_customer_profile(customer_id: str) -> dict:
    """Return a fictional customer profile by customer ID."""

    if not isinstance(customer_id, str) or not customer_id.strip():
        raise ValueError("Customer ID is required.")

    customer_id = customer_id.strip().upper()
    customer = CUSTOMERS.get(customer_id)

    if customer is None:
        raise ValueError(f"Customer '{customer_id}' was not found.")

    # Return a copy so callers cannot modify the stored record.
    return dict(customer)


def get_account_balance(customer_id: str) -> dict:
    """Return a fictional customer's account balance."""

    customer = get_customer_profile(customer_id)
    account_id = customer["account_id"]

    if account_id not in ACCOUNT_BALANCES:
        raise ValueError("Account balance is unavailable.")

    return {
        "customer_id": customer["customer_id"],
        "account_id": account_id,
        "balance": ACCOUNT_BALANCES[account_id],
        "currency": "INR",
        "environment": "Simulated",
    }


def get_transactions(customer_id: str, limit: int = 5) -> dict:
    """Return recent fictional transactions for a customer."""

    customer = get_customer_profile(customer_id)

    if isinstance(limit, bool) or not isinstance(limit, int):
        raise ValueError("Limit must be an integer.")

    if not 1 <= limit <= 20:
        raise ValueError("Limit must be between 1 and 20.")

    account_id = customer["account_id"]
    transactions = TRANSACTIONS.get(account_id)

    if transactions is None:
        raise ValueError("Transaction data is unavailable.")

    return {
        "customer_id": customer["customer_id"],
        "account_id": account_id,
        "transactions": [dict(txn) for txn in transactions[:limit]],
        "count": min(limit, len(transactions)),
        "environment": "Simulated",
    }

def assess_account_health(customer_id: str) -> dict:
    """Calculate simple account-health indicators using simulated data."""

    customer = get_customer_profile(customer_id)
    balance_result = get_account_balance(customer_id)

    monthly_income = customer["monthly_income"]
    monthly_emi = customer["monthly_existing_emi"]
    balance = balance_result["balance"]

    if monthly_income <= 0 or monthly_emi < 0 or balance < 0:
        raise ValueError("Invalid financial data for account health assessment.")

    emi_ratio = round((monthly_emi / monthly_income) * 100, 2)

    if emi_ratio <= 30:
        emi_status = "healthy"
        emi_reason = "Existing monthly EMI is at most 30% of income."
    elif emi_ratio <= 45:
        emi_status = "moderate"
        emi_reason = "Existing monthly EMI is between 30% and 45% of income."
    else:
        emi_status = "high"
        emi_reason = "Existing monthly EMI exceeds 45% of income."

    return {
        "customer_id": customer["customer_id"],
        "account_id": customer["account_id"],
        "balance_inr": balance,
        "monthly_income_inr": monthly_income,
        "monthly_existing_emi_inr": monthly_emi,
        "existing_emi_to_income_percent": emi_ratio,
        "emi_status": emi_status,
        "reason": emi_reason,
        "environment": "Simulated",
    }
