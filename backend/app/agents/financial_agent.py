def analyze_finances(customer):
    income = customer["monthly_income"]
    debt = customer["monthly_debt"]
    loan = customer["loan_amount"]

    if income <= 0 or debt < 0 or loan <= 0:
        raise ValueError("Invalid income, debt, or loan amount.")

    return {
        "debt_to_income_ratio": round(debt / income * 100, 2),
        "loan_to_income_ratio": round(loan / income, 2),
    }