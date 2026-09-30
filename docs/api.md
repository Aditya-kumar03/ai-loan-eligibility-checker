# REST API Specification

All backend endpoints are built using **FastAPI** with **Pydantic v2** validation. The interactive Swagger UI documentation is available at `/api/docs` when the server is running.

---

## 1. System Health
### `GET /api/health`
Returns the operational health of the application, active environment, and integration status for Claude and Google Sheets.

#### Response `200 OK`
```json
{
  "status": "healthy",
  "service": "AI Loan Eligibility Checker",
  "version": "1.0.0",
  "environment": "development",
  "integrations": {
    "claude_ai": {
      "configured": true,
      "model": "claude-3-7-sonnet-20250219",
      "mode": "Active"
    },
    "google_sheets": {
      "configured": false,
      "mode": "Local Only"
    }
  },
  "timestamp_utc": "2026-09-30T06:00:00.000000+00:00"
}
```

---

## 2. Loan Underwriting & Eligibility
### `POST /api/loan/analyze`
Evaluates complete borrower financial parameters, executes mathematical calculations, computes the 1000-point Estimated Financial Eligibility Score, and generates Claude AI analysis.

#### Request Body
```json
{
  "age": 28,
  "employment_type": "Salaried",
  "employment_experience_years": 4.0,
  "existing_bank_relationship": "Salary Account",
  "preferred_loan_type": "Personal Loan",
  "monthly_income": 75000,
  "existing_monthly_emi": 12000,
  "monthly_expenses": 25000,
  "loan_amount_required": 500000,
  "loan_tenure_months": 60,
  "expected_interest_rate": 12.0,
  "credit_score": 760,
  "total_credit_limit": 300000,
  "credit_used": 90000,
  "number_of_existing_loans": 1,
  "number_of_credit_cards": 2
}
```

#### Response `200 OK`
```json
{
  "session_id": "SES-7E9B4A1C",
  "status": "success",
  "eligibility_category": "Likely Eligible",
  "estimated_eligibility_score": 742,
  "score_breakdown": {
    "total_score": 742,
    "max_score": 1000,
    "credit_score_component": {
      "name": "Credit Bureau Profile",
      "points_awarded": 268.3,
      "max_points": 350.0,
      "rating": "Excellent",
      "explanation": "Bureau score of 760 is in the top-tier lending bracket."
    },
    "dti_component": { ... },
    "income_stability_component": { ... },
    "credit_utilization_component": { ... },
    "expense_buffer_component": { ... }
  },
  "metrics": {
    "current_dti_pct": 16.0,
    "proposed_emi": 11122.22,
    "total_emi_burden": 23122.22,
    "post_loan_dti_pct": 30.83,
    "total_monthly_obligations": 48122.22,
    "net_disposable_surplus": 26877.78,
    "credit_utilization_pct": 30.0,
    "loan_to_income_ratio": 0.56,
    "total_interest_payable": 167333.2,
    "total_repayment_amount": 667333.2
  },
  "deterministic_reasons": [
    "Your credit score of 760 is within a generally favorable range for prime interest rates.",
    "Your post-loan debt-to-income ratio (30.83%) represents a very manageable share of your income.",
    "Your credit utilization of 30.0% remains within the recommended 30% ceiling."
  ],
  "ai_analysis": {
    "summary": "Applicant demonstrates stable debt servicing capacity...",
    "eligibility_explanation": "With a post-loan DTI of 30.8% and bureau score of 760...",
    "strengths": [ ... ],
    "concerns": [ ... ],
    "recommendations": [ ... ],
    "risk_considerations": [ ... ],
    "questions_for_lender": [ ... ],
    "is_ai_generated": true,
    "model_used": "Anthropic claude-3-7-sonnet-20250219"
  },
  "disclaimer": "This tool provides estimates for educational and informational purposes only...",
  "sheets_synced": false
}
```

---

## 3. Credit Score Analyzer
### `POST /api/credit/analyze`
Evaluates revolving credit lines and bureau reference bands.

#### Request Body
```json
{
  "credit_score": 760,
  "total_credit_limit": 300000,
  "used_credit": 90000,
  "number_of_credit_cards": 2,
  "number_of_active_loans": 1,
  "monthly_income": 75000,
  "existing_monthly_emi": 12000
}
```

---

## 4. EMI Calculator
### `POST /api/emi/calculate`
Calculates reducing balance EMI and amortization schedule.

#### Request Body
```json
{
  "loan_amount": 500000,
  "interest_rate": 12.0,
  "tenure_value": 5,
  "tenure_type": "years"
}
```

---

## 5. AI Financial Tips
### `POST /api/ai/financial-tips`
Retrieves tailored financial guidance on 7 Indian BFSI topics.

#### Request Body
```json
{
  "topic": "Credit Score",
  "user_context": "Planning to apply for first home loan in 6 months"
}
```
