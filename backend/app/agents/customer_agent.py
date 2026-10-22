
def process_customer(data):
    name = str(data.get("name", "")).strip()
    employment = str(data.get("employmentType", "")).strip()

    if not name:
        raise ValueError("Customer name is required.")

    if employment not in ("Salaried", "Self-employed", "Unemployed"):
        raise ValueError("Invalid employment type.")

    try:
        income = float(data.get("monthlyIncome", 0))
        loan = float(data.get("loanAmount", 0))
        debt = float(data.get("monthlyDebt", 0))
        credit_score = int(data.get("creditScore", 0))
    except (ValueError, TypeError):
        raise ValueError("Please enter valid numeric values.")

    if income <= 0 or loan <= 0 or debt < 0:
        raise ValueError("Income and loan must be positive; debt cannot be negative.")

    if not 300 <= credit_score <= 900:
        raise ValueError("Credit score must be between 300 and 900.")

    return {
        "name": name,
        "employment": employment,
        "monthly_income": income,
        "loan_amount": loan,
        "monthly_debt": debt,
        "credit_score": credit_score,
    }
