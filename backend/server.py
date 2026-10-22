
from flask import Flask, jsonify, request
from flask_cors import CORS

from app.agents.customer_agent import process_customer
from app.agents.financial_agent import analyze_finances
from app.agents.loan_decision_agent import evaluate_decision
from app.agents.explanation_agent import explain_decision
from app.agents.supervisor_agent import route_request
from app.agents.banking_agent import handle_banking_request
from app.agents.gemini_interpreter import (
    interpret_banking_request,
    interpret_request_locally,
)
from app.agents.risk_agent import assess_transaction_risk
from app.agents.credit_agent import (
    evaluate_credit,
    find_counterfactuals,
)
from app.tools.customer_tools import get_customer_profile
from app.tools.execution_trace import run_with_trace


app = Flask(__name__)

CORS(
    app,
    resources={
        r"/*": {
            "origins": [
                "http://localhost:5173",
                "http://localhost:5174",
                "http://localhost:5175",
                "http://localhost:5176",
                "http://127.0.0.1:5173",
                "http://127.0.0.1:5174",
                "http://127.0.0.1:5175",
                "http://127.0.0.1:5176",
            ]
        }
    },
)


@app.get("/")
def home():
    return jsonify({
        "message": "Glass Box Loan Desk backend is running!",
        "status": "success",
        "environment": "Simulated",
    })


def _execute_workflow(request_type, customer_id, loan_amount):
    """Run a workflow and return (response_dict, status_code)."""

    try:
        routing = route_request(request_type)
    except (ValueError, TypeError) as exc:
        return {"error": str(exc)}, 400

    response_data = {
        "supervisor": "Supervisor Agent",
        **routing,
        "environment": "Simulated",
    }

    if routing["needs_clarification"]:
        return response_data, 200

    trace = []

    try:
        if request_type in ("account_lookup", "suspicious_txn"):
            banking_result, step = run_with_trace(
                agent_name="Banking Agent",
                tool_name="handle_banking_request",
                tool_function=handle_banking_request,
                request_type=request_type,
                customer_id=customer_id,
            )
            trace.append(step)
            response_data["banking_result"] = banking_result

            if request_type == "suspicious_txn":
                risk_result, step = run_with_trace(
                    agent_name="Risk Agent",
                    tool_name="assess_transaction_risk",
                    tool_function=assess_transaction_risk,
                    banking_result=banking_result,
                )
                trace.append(step)
                response_data["risk_result"] = risk_result

        elif request_type in ("loan_check", "what_if"):
            if not isinstance(customer_id, str) or not customer_id.strip():
                return {"error": "A valid customer_id is required."}, 400

            if (
                not isinstance(loan_amount, (int, float))
                or isinstance(loan_amount, bool)
                or loan_amount <= 0
            ):
                return {"error": "A positive loan_amount is required."}, 400

            profile, step = run_with_trace(
                agent_name="Banking Agent",
                tool_name="get_customer_profile",
                tool_function=get_customer_profile,
                customer_id=customer_id,
            )
            trace.append(step)

            customer = {
                "name": profile.get("name", "Unknown"),
                "employment_type": profile.get("employment_type"),
                "monthly_income": profile.get("monthly_income"),
                "monthly_debt": profile.get(
                    "monthly_existing_emi",
                    profile.get("monthly_debt", 0),
                ),
                "loan_amount": float(loan_amount),
                "credit_score": profile.get("credit_score"),
            }

            finances, step = run_with_trace(
                agent_name="Financial Agent",
                tool_name="analyze_finances",
                tool_function=analyze_finances,
                customer=customer,
            )
            trace.append(step)

            if request_type == "loan_check":
                credit_result, step = run_with_trace(
                    agent_name="Credit Agent",
                    tool_name="evaluate_credit",
                    tool_function=evaluate_credit,
                    customer=customer,
                    finances=finances,
                )
                trace.append(step)
                response_data["customer"] = customer
                response_data["financial_analysis"] = finances
                response_data["credit_result"] = credit_result

            else:
                what_if_result, step = run_with_trace(
                    agent_name="Credit Agent",
                    tool_name="find_counterfactuals",
                    tool_function=find_counterfactuals,
                    customer=customer,
                    finances=finances,
                )
                trace.append(step)
                response_data["customer"] = customer
                response_data["financial_analysis"] = finances
                response_data["what_if_result"] = what_if_result

        if trace:
            response_data["agent_trace"] = trace

        return response_data, 200

    except (ValueError, TypeError, KeyError) as exc:
        return {"error": str(exc)}, 400

    except Exception as exc:
        return {"error": "Request failed. Check the backend terminal."}, 500


@app.post("/interpret")
def interpret_request():
    data = request.get_json(silent=True) or {}
    message = data.get("message", "")

    if not isinstance(message, str) or not message.strip():
        return jsonify({"error": "Please enter a banking request."}), 400

    try:
        interpreted = interpret_banking_request(message)
    except (ValueError, RuntimeError):
        # Gemini unavailable or failed — fall back to local rules
        try:
            interpreted = interpret_request_locally(message)
        except ValueError as exc:
            return jsonify({"error": str(exc)}), 400

    if interpreted.get("needs_clarification"):
        return jsonify({
            "needs_clarification": True,
            "clarification": interpreted.get("clarification"),
            "request_type": interpreted.get("request_type"),
        })

    result, status = _execute_workflow(
        request_type=interpreted.get("request_type"),
        customer_id=interpreted.get("customer_id"),
        loan_amount=interpreted.get("loan_amount"),
    )
    result["interpreted_as"] = interpreted
    return jsonify(result), status


@app.post("/route-request")
def route_user_request():
    data = request.get_json(silent=True) or {}
    request_type = data.get("request_type")
    customer_id = data.get("customer_id")
    loan_amount = data.get("loan_amount", data.get("loanAmount"))

    result, status = _execute_workflow(request_type, customer_id, loan_amount)
    return jsonify(result), status


@app.post("/evaluate-loan")
def evaluate_loan():
    data = request.get_json(silent=True) or {}

    try:
        name = str(
            data.get("name")
            or data.get("customerName")
            or data.get("customer_name")
            or ""
        ).strip()

        income = float(
            data.get("monthlyIncome", data.get("monthly_income", 0))
        )

        loan_amount = float(
            data.get("loanAmount", data.get("loan_amount", 0))
        )

        monthly_debt = float(
            data.get(
                "monthlyDebt",
                data.get(
                    "monthly_debt",
                    data.get("monthly_existing_emi", 0),
                ),
            )
        )

        credit_score = int(
            data.get("creditScore", data.get("credit_score", 0))
        )

        employment = str(
            data.get("employmentType")
            or data.get("employment")
            or data.get("employment_type")
            or ""
        ).strip()

        if not name or not employment:
            return jsonify({
                "error": "Name and employment type are required."
            }), 400

        if income <= 0 or loan_amount <= 0 or monthly_debt < 0:
            return jsonify({
                "error": "Enter valid income, loan amount and debt values."
            }), 400

        if not 300 <= credit_score <= 900:
            return jsonify({
                "error": "Credit score must be between 300 and 900."
            }), 400

        customer_data = {
            **data,
            "name": name,
            "customerName": name,
            "customer_name": name,
            "monthly_income": income,
            "monthlyIncome": income,
            "loan_amount": loan_amount,
            "loanAmount": loan_amount,
            "monthly_debt": monthly_debt,
            "monthlyDebt": monthly_debt,
            "monthly_existing_emi": monthly_debt,
            "credit_score": credit_score,
            "creditScore": credit_score,
            "employment_type": employment,
            "employmentType": employment,
            "employment": employment,
        }

        trace = []

        customer, step = run_with_trace(
            agent_name="Customer Agent",
            tool_name="process_customer",
            tool_function=process_customer,
            data=customer_data,
        )
        trace.append(step)

        customer["name"] = name
        customer["monthly_income"] = income
        customer["loan_amount"] = loan_amount
        customer["monthly_debt"] = monthly_debt
        customer["credit_score"] = credit_score
        customer["employment_type"] = employment

        finances, step = run_with_trace(
            agent_name="Financial Agent",
            tool_name="analyze_finances",
            tool_function=analyze_finances,
            customer=customer,
        )
        trace.append(step)

        decision, step = run_with_trace(
            agent_name="Loan Decision Agent",
            tool_name="evaluate_decision",
            tool_function=evaluate_decision,
            customer=customer,
            finances=finances,
        )
        trace.append(step)

        result, step = run_with_trace(
            agent_name="Explanation Agent",
            tool_name="explain_decision",
            tool_function=explain_decision,
            customer=customer,
            finances=finances,
            decision=decision,
        )
        trace.append(step)

        if not isinstance(result, dict):
            raise TypeError(
                "The explanation agent must return a dictionary."
            )

        result["customerName"] = name
        result["loanAmount"] = loan_amount
        result["creditScore"] = credit_score
        result["environment"] = "Simulated"
        result["disclaimer"] = (
            "Demonstration only. This is not a real lending decision."
        )
        result["agent_trace"] = trace

        return jsonify(result)

    except (ValueError, TypeError, KeyError) as exc:
        return jsonify({
            "error": f"Invalid application data: {exc}"
        }), 400

    except Exception:
        app.logger.exception("Loan evaluation failed")
        return jsonify({
            "error": "Loan evaluation failed. Check the backend terminal."
        }), 500


if __name__ == "__main__":
    app.run(debug=True, port=5000)
