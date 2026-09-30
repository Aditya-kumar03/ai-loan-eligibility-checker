import pytest
from backend.app.services.calculator import (
    calculate_emi_exact,
    compute_financial_metrics,
    compute_eligibility_score,
    analyze_credit_profile,
    calculate_emi_tool
)
from backend.app.models.loan import LoanApplicationRequest
from backend.app.models.credit import CreditProfileRequest
from backend.app.models.emi import EMIRequest

def test_emi_exact_calculation():
    # Test standard loan: ₹5,00,000 at 12% for 5 years (60 months)
    # Formula: EMI = 500000 * 0.01 * (1.01^60) / (1.01^60 - 1) ≈ ₹11,122.22
    emi, interest, total = calculate_emi_exact(500000, 12.0, 60)
    assert 11120 <= emi <= 11125
    assert total == round(emi * 60, 2)
    assert interest == round(total - 500000, 2)

def test_emi_zero_interest():
    # 0% interest loan: ₹1,20,000 for 12 months = ₹10,000/month
    emi, interest, total = calculate_emi_exact(120000, 0.0, 12)
    assert emi == 10000.0
    assert interest == 0.0
    assert total == 120000.0

def test_emi_zero_or_negative_inputs():
    emi, interest, total = calculate_emi_exact(0, 10.0, 12)
    assert emi == 0.0
    assert interest == 0.0

    emi, interest, total = calculate_emi_exact(100000, 10.0, 0)
    assert emi == 0.0

def test_dti_and_metrics_calculation():
    req = LoanApplicationRequest(
        age=28,
        employment_type="Salaried",
        employment_experience_years=4.0,
        monthly_income=75000,
        existing_monthly_emi=12000,
        monthly_expenses=25000,
        loan_amount_required=500000,
        loan_tenure_months=60,
        expected_interest_rate=12.0,
        credit_score=760,
        total_credit_limit=300000,
        credit_used=90000,
        number_of_existing_loans=1,
        number_of_credit_cards=2
    )

    metrics = compute_financial_metrics(req)
    # Current DTI = (12000 / 75000) * 100 = 16.0%
    assert metrics.current_dti_pct == 16.0
    # Proposed EMI ~ 11122
    assert 11120 <= metrics.proposed_emi <= 11125
    # Total EMI burden = 12000 + ~11122 ≈ 23122
    assert 23120 <= metrics.total_emi_burden <= 23125
    # Post loan DTI = (23122 / 75000) * 100 ≈ 30.8%
    assert 30.0 <= metrics.post_loan_dti_pct <= 32.0
    # Credit utilization = (90000 / 300000) * 100 = 30.0%
    assert metrics.credit_utilization_pct == 30.0
    # Net surplus = 75000 - (23122 + 25000) ≈ 26878 > 0
    assert metrics.net_disposable_surplus > 20000

def test_eligibility_score_and_outcomes():
    # Strong profile -> Likely Eligible
    req_strong = LoanApplicationRequest(
        age=30,
        employment_type="Salaried",
        employment_experience_years=5.0,
        monthly_income=100000,
        existing_monthly_emi=5000,
        monthly_expenses=30000,
        loan_amount_required=400000,
        loan_tenure_months=36,
        expected_interest_rate=10.5,
        credit_score=780,
        total_credit_limit=200000,
        credit_used=20000,
        number_of_existing_loans=0,
        number_of_credit_cards=1
    )
    metrics_strong = compute_financial_metrics(req_strong)
    breakdown, category, reasons = compute_eligibility_score(req_strong, metrics_strong)

    assert breakdown.total_score >= 700
    assert category == "Likely Eligible"
    assert len(reasons) >= 3

    # Weak profile with high existing EMI > income -> Potentially Difficult
    req_weak = LoanApplicationRequest(
        age=24,
        employment_type="Other",
        employment_experience_years=0.5,
        monthly_income=25000,
        existing_monthly_emi=20000, # 80% DTI already
        monthly_expenses=15000,
        loan_amount_required=500000,
        loan_tenure_months=24,
        expected_interest_rate=18.0,
        credit_score=520,
        total_credit_limit=50000,
        credit_used=48000, # 96% utilization
        number_of_existing_loans=3,
        number_of_credit_cards=3
    )
    metrics_weak = compute_financial_metrics(req_weak)
    breakdown_weak, category_weak, _ = compute_eligibility_score(req_weak, metrics_weak)

    assert breakdown_weak.total_score < 540
    assert category_weak == "Potentially Difficult"

def test_credit_analyzer_service():
    req = CreditProfileRequest(
        credit_score=760,
        total_credit_limit=300000,
        used_credit=90000,
        number_of_credit_cards=2,
        number_of_active_loans=1,
        monthly_income=75000,
        existing_monthly_emi=12000
    )
    res = analyze_credit_profile(req)
    assert res.credit_score == 760
    assert res.credit_utilization_pct == 30.0
    assert res.reference_band.band_name == "Very Good"
    assert res.reference_band.range_label == "740–799"
    assert len(res.all_reference_ranges) == 5
    assert len(res.actionable_recommendations) >= 2

def test_emi_calculator_service():
    req = EMIRequest(
        loan_amount=1000000,
        interest_rate=8.5,
        tenure_value=10,
        tenure_type="years"
    )
    res = calculate_emi_tool(req)
    assert res.tenure_months == 120
    assert 12000 <= res.monthly_emi <= 12500
    assert res.principal_amount == 1000000
    assert len(res.amortization_schedule) == 10
