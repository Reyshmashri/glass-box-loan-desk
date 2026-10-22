
import { useState } from "react";
import "./App.css";

const API_URL = "http://127.0.0.1:5000";

const WORKFLOW_LABELS = {
  account_lookup: "Account Lookup",
  suspicious_txn: "Suspicious Transaction Review",
  loan_check: "Loan Eligibility Check",
  what_if: "What-If Analysis",
};

function Field({ label, value }) {
  return (
    <div className="field">
      <span className="field-label">{label}</span>
      <span className="field-value">{value}</span>
    </div>
  );
}

function DecisionBadge({ decision }) {
  const pass = decision === "Eligible for Consideration";
  return (
    <span className={`badge ${pass ? "badge-pass" : "badge-review"}`}>
      {decision}
    </span>
  );
}

function RuleRow({ rule }) {
  return (
    <div className={`rule-row ${rule.passed ? "rule-pass" : "rule-fail"}`}>
      <span className="rule-icon">{rule.passed ? "✓" : "✗"}</span>
      <div className="rule-body">
        <span className="rule-name">{rule.rule.replace(/_/g, " ")}</span>
        <span className="rule-reason">{rule.reason}</span>
      </div>
    </div>
  );
}

function CustomerCard({ customer }) {
  if (!customer) return null;
  return (
    <div className="info-card">
      <p className="info-card-title">👤 Customer Profile</p>
      <div className="fields">
        <Field label="Name" value={customer.name} />
        <Field label="Customer ID" value={customer.customer_id} />
        <Field label="Age" value={customer.age} />
        <Field label="Employment" value={customer.employment_type} />
        <Field label="Monthly Income" value={`₹${Number(customer.monthly_income).toLocaleString()}`} />
        <Field label="Monthly EMI" value={`₹${Number(customer.monthly_existing_emi ?? customer.monthly_debt ?? 0).toLocaleString()}`} />
        <Field label="Credit Score" value={customer.credit_score} />
      </div>
    </div>
  );
}

function AccountCard({ account }) {
  if (!account) return null;
  return (
    <div className="info-card">
      <p className="info-card-title">🏦 Account</p>
      <div className="fields">
        <Field label="Account ID" value={account.account_id} />
        <Field label="Balance" value={`₹${Number(account.balance).toLocaleString()}`} />
        <Field label="Currency" value={account.currency} />
      </div>
    </div>
  );
}

function TransactionsCard({ txnData }) {
  if (!txnData) return null;
  const txns = txnData.transactions || [];
  return (
    <div className="info-card">
      <p className="info-card-title">💳 Transactions ({txns.length})</p>
      {txns.length === 0 ? (
        <p className="muted">No transactions found.</p>
      ) : (
        txns.map((t) => (
          <div key={t.transaction_id} className="txn-row">
            <span className="txn-id">{t.transaction_id}</span>
            <span className="txn-desc">{t.description}</span>
            <span className={`txn-amount ${t.type === "credit" ? "credit" : "debit"}`}>
              {t.type === "credit" ? "+" : "-"}₹{Number(t.amount).toLocaleString()}
            </span>
            <span className="txn-status">{t.status}</span>
          </div>
        ))
      )}
    </div>
  );
}

function CreditCard({ creditResult }) {
  if (!creditResult) return null;
  return (
    <div className="info-card">
      <p className="info-card-title">📋 Credit Evaluation</p>
      <div style={{ marginBottom: 14 }}>
        <DecisionBadge decision={creditResult.decision} />
      </div>
      <div className="rules-list">
        {(creditResult.rules_checked || []).map((r) => (
          <RuleRow key={r.rule} rule={r} />
        ))}
      </div>
    </div>
  );
}

function RiskCard({ riskResult }) {
  if (!riskResult) return null;
  const safe = riskResult.risk_level === "No rule triggered";
  return (
    <div className="info-card">
      <p className="info-card-title">🔍 Risk Review</p>
      <div style={{ marginBottom: 12 }}>
        <span className={`badge ${safe ? "badge-pass" : "badge-review"}`}>
          {riskResult.risk_level}
        </span>
      </div>
      {riskResult.findings && riskResult.findings.length > 0 && (
        <div className="rules-list">
          {riskResult.findings.map((f, i) => (
            <div key={i} className="rule-row rule-fail">
              <span className="rule-icon">⚠</span>
              <div className="rule-body">
                <span className="rule-name">{f.transaction_id}</span>
                <span className="rule-reason">₹{Number(f.amount).toLocaleString()} — {f.rule}</span>
              </div>
            </div>
          ))}
        </div>
      )}
      {(riskResult.rules_checked || []).map((r) => (
        <p key={r.rule} className="muted" style={{ marginTop: 10 }}>
          Rule checked: {r.rule.replace(/_/g, " ")} — threshold ₹{Number(r.threshold_inr).toLocaleString()}
        </p>
      ))}
      <p className="disclaimer">{riskResult.disclaimer}</p>
    </div>
  );
}

function WhatIfCard({ whatIfResult }) {
  if (!whatIfResult) return null;
  return (
    <div className="info-card">
      <p className="info-card-title">💡 What-If Suggestions</p>
      <div style={{ marginBottom: 12 }}>
        <span className="badge badge-review">{whatIfResult.current_decision}</span>
      </div>
      {whatIfResult.suggestions.length === 0 ? (
        <p className="muted">No improvements needed — already eligible.</p>
      ) : (
        <ul className="suggestion-list">
          {whatIfResult.suggestions.map((s, i) => (
            <li key={i} className="suggestion-item">
              <span className="suggestion-icon">→</span>
              {s.suggestion}
            </li>
          ))}
        </ul>
      )}
      {whatIfResult.note && <p className="disclaimer">{whatIfResult.note}</p>}
    </div>
  );
}

function FinancialCard({ finances }) {
  if (!finances) return null;
  return (
    <div className="info-card">
      <p className="info-card-title">📊 Financial Analysis</p>
      <div className="fields">
        <Field label="Debt-to-Income Ratio" value={`${finances.debt_to_income_ratio}%`} />
        <Field label="Loan-to-Income Ratio" value={`${finances.loan_to_income_ratio}×`} />
      </div>
    </div>
  );
}

function BankingResultCards({ bankingResult }) {
  if (!bankingResult) return null;
  return (
    <>
      <CustomerCard customer={bankingResult.customer} />
      <AccountCard account={bankingResult.account} />
      <TransactionsCard txnData={bankingResult.transactions} />
      {bankingResult.account_health && (
        <div className="info-card">
          <p className="info-card-title">❤️ Account Health</p>
          <div className="fields">
            <Field label="EMI Status" value={bankingResult.account_health.emi_status} />
            <Field label="EMI to Income" value={`${bankingResult.account_health.existing_emi_to_income_percent}%`} />
            <Field label="Balance" value={`₹${Number(bankingResult.account_health.balance_inr).toLocaleString()}`} />
          </div>
          <p className="muted" style={{ marginTop: 8 }}>{bankingResult.account_health.reason}</p>
        </div>
      )}
    </>
  );
}



function App() {
  const [activeTab, setActiveTab] = useState("nl");

  const [form, setForm] = useState({
    customerName: "",
    monthlyIncome: "",
    loanAmount: "",
    monthlyDebt: "",
    employment: "Salaried",
    creditScore: "",
  });

  const [result, setResult] = useState(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(false);

  const [nlMessage, setNlMessage] = useState("");
  const [nlResult, setNlResult] = useState(null);
  const [nlError, setNlError] = useState("");
  const [nlLoading, setNlLoading] = useState(false);

  const [workflow, setWorkflow] = useState("account_lookup");
  const [customerId, setCustomerId] = useState("CUST-1001");
  const [workflowLoanAmount, setWorkflowLoanAmount] = useState("200000");
  const [workflowResult, setWorkflowResult] = useState(null);
  const [workflowError, setWorkflowError] = useState("");
  const [workflowLoading, setWorkflowLoading] = useState(false);

  function handleChange(event) {
    const { name, value } = event.target;
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError("");
    setResult(null);
    setLoading(true);
    try {
      const response = await fetch(`${API_URL}/evaluate-loan`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
          name: form.customerName,
          monthlyIncome: Number(form.monthlyIncome),
          loanAmount: Number(form.loanAmount),
          monthlyDebt: Number(form.monthlyDebt),
          employmentType: form.employment,
          creditScore: Number(form.creditScore),
        }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "Unable to evaluate the application.");
      setResult(data);
    } catch (err) {
      setError(err.message || "Could not connect to Flask. Check that the backend is running.");
    } finally {
      setLoading(false);
    }
  }

  async function handleNlSubmit(event) {
    event.preventDefault();
    setNlError("");
    setNlResult(null);
    setNlLoading(true);
    try {
      const response = await fetch(`${API_URL}/interpret`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ message: nlMessage }),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "The request could not be interpreted.");
      setNlResult(data);
    } catch (err) {
      setNlError(err.message || "Could not connect to Flask. Check that the backend is running.");
    } finally {
      setNlLoading(false);
    }
  }

  async function handleWorkflowSubmit(event) {
    event.preventDefault();
    setWorkflowError("");
    setWorkflowResult(null);
    setWorkflowLoading(true);
    const body = { request_type: workflow };
    if (workflow !== "unknown") {
      if (!customerId.trim()) {
        setWorkflowError("Please enter a customer ID.");
        setWorkflowLoading(false);
        return;
      }
      body.customer_id = customerId.trim();
    }
    if (workflow === "loan_check" || workflow === "what_if") {
      const amount = Number(workflowLoanAmount);
      if (!Number.isFinite(amount) || amount <= 0) {
        setWorkflowError("Enter a valid loan amount greater than zero.");
        setWorkflowLoading(false);
        return;
      }
      body.loan_amount = amount;
    }
    try {
      const response = await fetch(`${API_URL}/route-request`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify(body),
      });
      const data = await response.json();
      if (!response.ok) throw new Error(data.error || "The workflow failed.");
      setWorkflowResult(data);
    } catch (err) {
      setWorkflowError(err.message || "Could not connect to Flask. Check that the backend is running.");
    } finally {
      setWorkflowLoading(false);
    }
  }

  return (
    <main className="app">
      <p className="tag">SIMULATED BANKING ENVIRONMENT</p>
      <h1>Glass Box Loan Desk</h1>
      <p>Transparent banking decisions, explained rule by rule.</p>

      <div className="tab-bar">
        <button type="button" className={`tab-btn${activeTab === "nl" ? " tab-active" : ""}`} onClick={() => setActiveTab("nl")}>💬 Assistant</button>
        <button type="button" className={`tab-btn${activeTab === "loan" ? " tab-active" : ""}`} onClick={() => setActiveTab("loan")}>📝 Loan Application</button>
        <button type="button" className={`tab-btn${activeTab === "workbench" ? " tab-active" : ""}`} onClick={() => setActiveTab("workbench")}>🔧 Agent Workbench</button>
      </div>

      {/* ── Natural Language Panel ── */}
      {activeTab === "nl" && <section className="loan-card">
        <h2>Natural Language Banking Assistant</h2>
        <p>Type a banking request in plain English. The AI interpreter routes it to the right specialist agents.</p>

        <form onSubmit={handleNlSubmit}>
          <label style={{ gridColumn: "1 / -1" }}>
            Your request
            <input
              value={nlMessage}
              onChange={(e) => setNlMessage(e.target.value)}
              required
              placeholder='e.g. "Check loan eligibility for CUST-1002 for ₹300000"'
            />
          </label>
          <button type="submit" disabled={nlLoading}>
            {nlLoading ? "Interpreting..." : "Send Request"}
          </button>
        </form>

        {nlError && <p className="error">{nlError}</p>}

        {nlResult && (
          <section className="result">
            {nlResult.needs_clarification ? (
              <>
                <h3>Clarification Needed</h3>
                <p>{nlResult.clarification}</p>
              </>
            ) : (
              <>
                <div className="interpreted-banner">
                  <span className="interpreted-label">Interpreted as</span>
                  <span className="interpreted-workflow">
                    {WORKFLOW_LABELS[nlResult.interpreted_as?.request_type] ?? nlResult.interpreted_as?.request_type}
                  </span>
                  {nlResult.interpreted_as?.customer_id && (
                    <span className="interpreted-chip">{nlResult.interpreted_as.customer_id}</span>
                  )}
                  {nlResult.interpreted_as?.loan_amount && (
                    <span className="interpreted-chip">
                      ₹{Number(nlResult.interpreted_as.loan_amount).toLocaleString()}
                    </span>
                  )}
                </div>

                <BankingResultCards bankingResult={nlResult.banking_result} />
                <RiskCard riskResult={nlResult.risk_result} />
                <CreditCard creditResult={nlResult.credit_result} />
                <FinancialCard finances={nlResult.financial_analysis} />
                <WhatIfCard whatIfResult={nlResult.what_if_result} />

              </>
            )}
          </section>
        )}
      </section>}

      {/* ── Loan Application Panel ── */}
      {activeTab === "loan" && <section className="loan-card">
        <h2>Customer Loan Application</h2>
        <p>Enter applicant details to evaluate a loan using the standalone application workflow.</p>

        <form onSubmit={handleSubmit}>
          <label>
            Customer Name
            <input name="customerName" value={form.customerName} onChange={handleChange} required placeholder="Enter customer name" />
          </label>
          <label>
            Monthly Income (₹)
            <input name="monthlyIncome" type="number" min="1" value={form.monthlyIncome} onChange={handleChange} required placeholder="e.g. 40000" />
          </label>
          <label>
            Loan Amount Requested (₹)
            <input name="loanAmount" type="number" min="1" value={form.loanAmount} onChange={handleChange} required placeholder="e.g. 200000" />
          </label>
          <label>
            Existing Monthly Debt Payments (₹)
            <input name="monthlyDebt" type="number" min="0" value={form.monthlyDebt} onChange={handleChange} required placeholder="e.g. 5000" />
          </label>
          <label>
            Employment Type
            <select name="employment" value={form.employment} onChange={handleChange}>
              <option value="Salaried">Salaried</option>
              <option value="Self-employed">Self-employed</option>
              <option value="Unemployed">Unemployed</option>
            </select>
          </label>
          <label>
            Credit Score (300–900)
            <input name="creditScore" type="number" min="300" max="900" value={form.creditScore} onChange={handleChange} required placeholder="e.g. 750" />
          </label>
          <button type="submit" disabled={loading}>
            {loading ? "Evaluating..." : "Evaluate Loan"}
          </button>
        </form>

        {error && <p className="error">{error}</p>}

        {result && (
          <>
            <section className="result">
              <div className="info-card">
                <p className="info-card-title">📋 Loan Decision</p>
                <div style={{ marginBottom: 14 }}>
                  <DecisionBadge decision={result.decision} />
                </div>
                <div className="fields">
                  <Field label="Customer" value={result.customerName} />
                  <Field label="Loan Amount" value={`₹${Number(result.loanAmount).toLocaleString()}`} />
                  <Field label="Credit Score" value={result.creditScore} />
                  <Field label="Debt-to-Income Ratio" value={`${result.debtToIncomeRatio}%`} />
                </div>
                <ul className="suggestion-list" style={{ marginTop: 14 }}>
                  {(result.reasons || []).map((reason, i) => (
                    <li key={i} className="suggestion-item">
                      <span className="suggestion-icon">•</span>
                      {reason}
                    </li>
                  ))}
                </ul>
                <p className="disclaimer">{result.disclaimer}</p>
              </div>
            </section>

          </>
        )}
      </section>}

      {/* ── Supervisor Workbench Panel ── */}
      {activeTab === "workbench" && <section className="loan-card">
        <h2>Supervisor Agent Workbench</h2>
        <p>Choose a workflow to retrieve mock banking information, review risk rules, or analyze loan eligibility.</p>

        <form onSubmit={handleWorkflowSubmit}>
          <label>
            Select Workflow
            <select value={workflow} onChange={(e) => { setWorkflow(e.target.value); setWorkflowResult(null); setWorkflowError(""); }}>
              <option value="account_lookup">Account Lookup</option>
              <option value="suspicious_txn">Suspicious Transaction Review</option>
              <option value="loan_check">Loan Check</option>
              <option value="what_if">What-If Analysis</option>
              <option value="unknown">Unknown Request Test</option>
            </select>
          </label>

          {workflow !== "unknown" && (
            <label>
              Mock Customer ID
              <select value={customerId} onChange={(e) => setCustomerId(e.target.value)}>
                <option value="CUST-1001">CUST-1001 — Aarav Sharma</option>
                <option value="CUST-1002">CUST-1002 — Meera Iyer</option>
                <option value="CUST-1003">CUST-1003 — Kabir Rao</option>
              </select>
            </label>
          )}

          {(workflow === "loan_check" || workflow === "what_if") && (
            <label>
              Requested Loan Amount (₹)
              <input type="number" min="1" value={workflowLoanAmount} onChange={(e) => setWorkflowLoanAmount(e.target.value)} required />
            </label>
          )}

          <button type="submit" disabled={workflowLoading}>
            {workflowLoading ? "Running Workflow..." : "Run Workflow"}
          </button>
        </form>

        {workflowError && <p className="error">{workflowError}</p>}

        {workflowResult && (
          <section className="result">
            <div className="interpreted-banner">
              <span className="interpreted-label">Workflow</span>
              <span className="interpreted-workflow">
                {WORKFLOW_LABELS[workflowResult.request_type] ?? workflowResult.request_type}
              </span>
              {(workflowResult.agents || []).length > 0 && (
                <span className="interpreted-chip">
                  {workflowResult.agents.join(" → ")}
                </span>
              )}
            </div>

            {workflowResult.needs_clarification && (
              <p className="muted" style={{ marginTop: 12 }}>
                This request is not recognized. Please select a supported workflow.
              </p>
            )}

            <BankingResultCards bankingResult={workflowResult.banking_result} />
            <RiskCard riskResult={workflowResult.risk_result} />
            <CreditCard creditResult={workflowResult.credit_result} />
            <FinancialCard finances={workflowResult.financial_analysis} />
            <WhatIfCard whatIfResult={workflowResult.what_if_result} />

          </section>
        )}
      </section>}

      <p className="note">
        Demonstration only. This prototype uses simulated customer data and rule-based assessments, not real bank decisions.
      </p>
    </main>
  );
}

export default App;
