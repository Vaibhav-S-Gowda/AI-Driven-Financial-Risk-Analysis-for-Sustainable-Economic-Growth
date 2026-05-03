# Enterprise Credit Risk & Decision Intelligence Architecture

This document outlines the architectural roadmap to evolve the current FinRisk AI dashboard into a production-grade, decision-intelligence system suitable for enterprise banks and fintechs.

## 1. Decision Intelligence
Moving beyond pure ML predictions (Probability of Default, PD) to actionable business outcomes.

### Implementation Strategy
*   **Approval Logic:** Implement a tiered decision matrix.
    *   `PD < 0.10`: Auto-Approve (Fast-track)
    *   `0.10 <= PD <= 0.40`: Manual Review (Referred to underwriters)
    *   `PD > 0.40`: Auto-Reject
*   **Dynamic Risk-Based Pricing:** Output customized interest rates and credit limits based on the continuous risk score.
*   **Pseudo-code (Decision Engine):**
```python
def generate_decision(pd_score, annual_income, requested_amount):
    # Base configuration
    base_rate = 5.5  # 5.5% base interest
    max_ltv = 0.30   # Max 30% of income 

    if pd_score < 0.10:
        decision = "Auto-Approve"
        approved_limit = min(annual_income * max_ltv, requested_amount)
        interest_rate = base_rate + (pd_score * 20) # Low risk premium
        
    elif pd_score > 0.40:
        decision = "Auto-Reject"
        approved_limit = 0
        interest_rate = None
        
    else:
        decision = "Manual Review"
        approved_limit = min(annual_income * (max_ltv - 0.1), requested_amount)
        interest_rate = base_rate + (pd_score * 35) # High risk premium
        
    return {"decision": decision, "limit": approved_limit, "rate": interest_rate}
```

## 2. Explainability (Local + Global)
Regulatory compliance (like GDPR/FCRA) requires providing adverse action reasons.

### Implementation Strategy
*   **Local Explainability:** Use `shap.TreeExplainer` for individual applicants. Render a SHAP waterfall plot in the UI to show exactly how base probability was shifted by specific features (e.g., `+12% due to Debt-to-Income = 45%`).
*   **Counterfactual Reasoning:** Implement the `DiCE` (Diverse Counterfactual Explanations) library.
    *   *Output:* "If the applicant's credit card utilization decreases by 12%, their application would be Approved."
*   **UI Component:** A dedicated "Explain Decision" modal on the Applicant Detail View containing the Waterfall plot and the "Path to Approval" (Counterfactuals).

## 3. Portfolio & Risk Analytics
Aggregate risk metrics for Chief Risk Officers (CROs) and Portfolio Managers.

### Implementation Strategy
*   **Expected Loss (EL):** $EL = PD \times LGD \times EAD$
    *   *PD:* From our ML model.
    *   *LGD (Loss Given Default):* Assumed 45% for unsecured personal loans.
    *   *EAD (Exposure at Default):* The loan amount.
*   **Concentration Risk:** Calculate the Herfindahl-Hirschman Index (HHI) across sectors or geographic regions to ensure the portfolio isn't over-exposed to a single demographic.
*   **UI Component:** Sunburst charts for portfolio segmentation (e.g., Sector -> Risk Tier -> Default Volume).

## 4. Time-Series & Monitoring
Models degrade over time. Continuous monitoring is required for production readiness.

### Implementation Strategy
*   **Drift Detection:** Integrate `Evidently AI`.
    *   Compute **Population Stability Index (PSI)** for input features (Data Drift).
    *   Compute drift on output predictions (Concept Drift).
*   **Early Warning Signals (EWS):** Calculate rolling 7-day Z-scores on the volume of "Auto-Reject" applications. If $Z > 2.0$, flag a potential macro-economic shift or targeted fraud attack.

## 5. What-If Simulation
Empower underwriters to test scenarios during manual reviews.

### Implementation Strategy
*   **Backend Logic:** Fast, stateless inference endpoint.
```python
@app.post("/api/simulate")
def simulate_applicant(features: ApplicantFeatures):
    # 1. Run ML Prediction
    pd_score = model.predict_proba([features.to_array()])[0][1]
    
    # 2. Run Business Rules
    decision_payload = generate_decision(pd_score, features.income, features.amount)
    
    # 3. Generate SHAP for the simulated data
    shap_values = get_shap_explanation(model, features)
    
    return {
        "pd_score": pd_score, 
        "decision": decision_payload, 
        "top_drivers": shap_values
    }
```
*   **UI Component:** A Streamlit `st.sidebar` or modal with sliders for continuous variables (Income, Loan Amount) and dropdowns for categoricals. Re-run simulation `on_change`.

## 6. Fraud Risk Layer
Credit risk assumes the applicant is telling the truth. Fraud risk verifies it.

### Implementation Strategy
*   **Anomaly Detection:** Train an `Isolation Forest` or an Autoencoder on behavioral metadata (time taken to fill application, IP address velocity, device type).
*   **Unified Scoring:**
    *   $Risk_{Total} = (w_1 \times PD) + (w_2 \times Anomaly Score)$
    *   If Anomaly Score > 95th percentile, automatically route to "Fraud Investigation" queue regardless of Credit PD.

## 7. Model Governance
For auditability and regulatory scrutiny.

### Implementation Strategy
*   **Model Registry:** Use `MLflow` to track model versions, hyperparameters, and training artifacts.
*   **Fairness & Bias:** Calculate the **Disparate Impact Ratio (DIR)**.
    *   $DIR = \frac{Approval\ Rate\ (Protected\ Class)}{Approval\ Rate\ (Unprotected\ Class)}$
    *   Establish a CI/CD pipeline check: If DIR < 0.8 (Four-Fifths Rule), fail the model deployment.

## 8. Alerting & Automation

### Implementation Strategy
*   **Orchestration:** Use `Apache Airflow` or `Celery` to run batch jobs at midnight.
*   **Webhooks:** If `Evidently AI` detects PSI > 0.2 (significant drift) or EWS triggers, fire a webhook to Slack/PagerDuty.
```python
def alert_slack(message):
    requests.post(SLACK_WEBHOOK_URL, json={"text": f"🚨 RISK ALERT: {message}"})
```

## 9. Data Quality Layer
Garbage in, garbage out.

### Implementation Strategy
*   **Validation:** Use `Great Expectations` to define strict schemas.
    *   Expect `annual_income` to be between \$10,000 and \$5,000,000.
    *   Expect missing value percentage for `employment_length` to be < 5%.
*   **UI Component:** A "Data Health" indicator light (Green/Yellow/Red) in the top nav of the dashboard.

## 10. UI/UX Improvements (Streamlit)
Restructure the application to support multiple personas.

### Implementation Strategy
*   **Role-Based Views (Sidebar Navigation):**
    1.  **Executive View:** High-level KPIs (Total EL, Approval Rate %, Active Drift Alerts).
    2.  **Portfolio Analyst View:** The current grid layout (Donut charts, Risk vs ESG, Concentration risk).
    3.  **Underwriter / Applicant View:** A search bar to load a specific Application ID -> shows applicant details, SHAP waterfall, Counterfactuals, and the What-If Simulator.
*   **Streamlit Layout Tip:** Use `st.columns`, `st.expander`, and `st.tabs` heavily to prevent vertical scrolling fatigue. Use `st.metric` with deltas for KPIs.

## 11. Technical Implementation
Transitioning from a prototype to a scalable architecture.

### Implementation Strategy
*   **Inference Layer:** Separate the ML model from Streamlit. Wrap the model in `FastAPI` or `BentoML` and deploy via Docker. Streamlit simply makes REST API calls.
*   **Storage:** 
    *   *Features:* PostgreSQL (Relational applicant data).
    *   *Logs:* Elasticsearch / MongoDB (Storing every prediction request and SHAP value for historical audit).
*   **Tech Stack:** `scikit-learn` / `xgboost` (Modeling), `SHAP` / `DiCE` (XAI), `Evidently` (Monitoring), `FastAPI` (Backend), `Streamlit` -> eventually `React/Next.js` (Frontend).

## 12. Bonus (Differentiation for Interviews)

### AI Underwriting Assistant (LLM Integration)
Integrate `LangChain` with an LLM (e.g., GPT-4 / Claude) to translate complex SHAP arrays and business rules into a human-readable adverse action summary.
*   **Prompt Architecture:** Feed the LLM the applicant features, the model's PD, the SHAP values, and the business rules JSON.
*   **Output Example:** *"The applicant was flagged for Manual Review. While their income ($85,000) is strong, the ML model identified their high Debt-to-Income ratio (42%) and short employment history (1.2 years) as primary risk drivers. Furthermore, the anomaly detection engine flagged this application due to a velocity rule (3 applications from the same IP in 24 hours)."*

### Network Risk via Graph Neural Networks (GNN)
Implement `NetworkX` or `PyTorch Geometric`. Represent applicants as nodes and shared attributes (Phone, Address, IP) as edges. A GNN can detect synthetic identity rings—if Applicant A is connected to a known default (Applicant B) via a shared IP address, Applicant A's risk score is dynamically inflated. This shows immense maturity in fraud architecture.
