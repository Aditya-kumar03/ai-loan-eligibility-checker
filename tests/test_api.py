import pytest
from fastapi.testclient import TestClient
from backend.main import app

client = TestClient(app)

def test_health_endpoint():
    response = client.get("/api/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert "integrations" in data
    assert "claude_ai" in data["integrations"]

def test_loan_analyze_endpoint():
    payload = {
        "age": 28,
        "employment_type": "Salaried",
        "employment_experience_years": 4.0,
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
    response = client.post("/api/loan/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "success"
    assert "estimated_eligibility_score" in data
    assert "metrics" in data
    assert "ai_analysis" in data
    assert "disclaimer" in data
    assert len(data["deterministic_reasons"]) >= 3

def test_loan_analyze_invalid_input():
    # Negative income should fail validation
    payload = {
        "age": 28,
        "employment_type": "Salaried",
        "monthly_income": -5000,
        "loan_amount_required": 500000,
        "loan_tenure_months": 60,
        "expected_interest_rate": 12.0,
        "credit_score": 760
    }
    response = client.post("/api/loan/analyze", json=payload)
    assert response.status_code == 422 # Pydantic validation error

def test_credit_analyze_endpoint():
    payload = {
        "credit_score": 750,
        "total_credit_limit": 200000,
        "used_credit": 40000,
        "number_of_credit_cards": 2,
        "number_of_active_loans": 0,
        "monthly_income": 60000,
        "existing_monthly_emi": 0
    }
    response = client.post("/api/credit/analyze", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["credit_utilization_pct"] == 20.0
    assert data["reference_band"]["band_name"] == "Very Good"

def test_emi_calculate_endpoint():
    payload = {
        "loan_amount": 500000,
        "interest_rate": 10.0,
        "tenure_value": 5,
        "tenure_type": "years"
    }
    response = client.post("/api/emi/calculate", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["tenure_months"] == 60
    assert data["monthly_emi"] > 0
    assert len(data["amortization_schedule"]) == 5

def test_financial_tips_endpoint():
    payload = {
        "topic": "Credit Score",
        "user_context": "Planning to apply for first home loan in 6 months"
    }
    response = client.post("/api/ai/financial-tips", json=payload)
    assert response.status_code == 200
    data = response.json()
    assert data["topic"] == "Credit Score"
    assert len(data["tips"]) >= 2
    assert "disclaimer" in data

def test_feedback_endpoint():
    payload = {
        "tool_name": "loan_eligibility",
        "rating": 5,
        "comments": "Very transparent scoring engine."
    }
    response = client.post("/api/feedback", json=payload)
    assert response.status_code == 200
    assert response.json()["status"] == "received"
