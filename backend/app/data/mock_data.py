
# All records in this file are fictional.
# They are for demonstration only, not real banking data.

CUSTOMERS = {
    "CUST-1001": {
        "customer_id": "CUST-1001",
        "name": "Aarav Sharma",
        "age": 29,
        "monthly_income": 65000,
        "employment_type": "Salaried",
        "monthly_existing_emi": 8000,
        "credit_score": 760,
        "account_id": "ACC-2001",
    },
    "CUST-1002": {
        "customer_id": "CUST-1002",
        "name": "Meera Iyer",
        "age": 34,
        "monthly_income": 42000,
        "employment_type": "Self-employed",
        "monthly_existing_emi": 12000,
        "credit_score": 680,
        "account_id": "ACC-2002",
    },
    "CUST-1003": {
        "customer_id": "CUST-1003",
        "name": "Kabir Rao",
        "age": 25,
        "monthly_income": 28000,
        "employment_type": "Salaried",
        "monthly_existing_emi": 2000,
        "credit_score": 610,
        "account_id": "ACC-2003",
    },
}

# Fictional account balances for the simulated environment.
ACCOUNT_BALANCES = {
    "ACC-2001": 125000.00,
    "ACC-2002": 48500.00,
    "ACC-2003": 9200.00,
}

# Fictional transactions for demonstration only.
TRANSACTIONS = {
    "ACC-2001": [
        {"transaction_id": "T-1042", "type": "debit", "amount": 8500.00, "description": "Online purchase", "status": "completed"},
        {"transaction_id": "T-1041", "type": "credit", "amount": 45000.00, "description": "Salary credit", "status": "completed"},
        {"transaction_id": "T-1040", "type": "debit", "amount": 2200.00, "description": "Utility payment", "status": "completed"},
        {"transaction_id": "T-1039", "type": "debit", "amount": 1500.00, "description": "Grocery purchase", "status": "completed"},
        {"transaction_id": "T-1038", "type": "credit", "amount": 5000.00, "description": "Refund", "status": "completed"},
    ],
    "ACC-2002": [
        {"transaction_id": "T-2042", "type": "debit", "amount": 3000.00, "description": "Rent payment", "status": "completed"},
        {"transaction_id": "T-2041", "type": "credit", "amount": 18000.00, "description": "Business income", "status": "completed"},
    ],
    "ACC-2003": [
        {"transaction_id": "T-3042", "type": "debit", "amount": 700.00, "description": "Food purchase", "status": "completed"},
    ],
}
