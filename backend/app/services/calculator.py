import math
from typing import Tuple, List, Dict, Any
from backend.app.models.loan import (
    LoanApplicationRequest,
    FinancialMetrics,
    EligibilityScoreBreakdown,
    ScoreComponent
)
from backend.app.models.emi import EMIRequest, EMIResponse, AmortizationYear
from backend.app.models.credit import (
    CreditProfileRequest,
    CreditAnalysisResponse,
    CreditBandInfo
)

DISCLAIMER_TEXT = (
    "This tool provides estimates for educational and informational purposes only. "
    "Actual loan approval, interest rates, eligibility, and credit decisions are determined "
    "by banks/NBFCs and may depend on additional factors."
)

def calculate_emi_exact(principal: float, annual_rate_pct: float, tenure_months: int) -> Tuple[float, float, float]:
    """
    Standard reducing balance EMI formula:
    EMI = P * r * (1+r)^n / ((1+r)^n - 1)
    where:
    P = Principal loan amount
    r = Monthly interest rate (annual_rate_pct / (12 * 100))
    n = Number of monthly installments
    """
    if principal <= 0 or tenure_months <= 0:
        return 0.0, 0.0, 0.0

    if annual_rate_pct <= 0:
        monthly_emi = round(principal / tenure_months, 2)
        total_payment = round(principal, 2)
        total_interest = 0.0
        return monthly_emi, total_interest, total_payment

    monthly_rate = (annual_rate_pct / 100.0) / 12.0
    power_term = math.pow(1.0 + monthly_rate, tenure_months)

    denominator = power_term - 1.0
    if denominator == 0:
        monthly_emi = round(principal / tenure_months, 2)
    else:
        monthly_emi = round((principal * monthly_rate * power_term) / denominator, 2)

    total_payment = round(monthly_emi * tenure_months, 2)
    total_interest = round(max(0.0, total_payment - principal), 2)

    return monthly_emi, total_interest, total_payment

def calculate_amortization_schedule(principal: float, annual_rate_pct: float, tenure_months: int) -> List[AmortizationYear]:
    """
    Builds year-by-year amortization breakdown.
    """
    monthly_emi, _, _ = calculate_emi_exact(principal, annual_rate_pct, tenure_months)
    monthly_rate = (annual_rate_pct / 100.0) / 12.0 if annual_rate_pct > 0 else 0.0

    schedule: List[AmortizationYear] = []
    balance = principal
    total_years = math.ceil(tenure_months / 12.0)

    month_idx = 0
    for year in range(1, total_years + 1):
        year_principal = 0.0
        year_interest = 0.0
        year_payment = 0.0

        for _ in range(12):
            if month_idx >= tenure_months or balance <= 0:
                break
            month_idx += 1

            if monthly_rate > 0:
                interest_month = balance * monthly_rate
                principal_month = min(balance, monthly_emi - interest_month)
                payment_month = principal_month + interest_month
            else:
                interest_month = 0.0
                principal_month = min(balance, monthly_emi)
                payment_month = principal_month

            balance = max(0.0, balance - principal_month)
            year_principal += principal_month
            year_interest += interest_month
            year_payment += payment_month

        schedule.append(AmortizationYear(
            year=year,
            principal_paid=round(year_principal, 2),
            interest_paid=round(year_interest, 2),
            total_payment_year=round(year_payment, 2),
            remaining_balance=round(balance, 2)
        ))

    return schedule

def compute_financial_metrics(req: LoanApplicationRequest) -> FinancialMetrics:
    """
    Calculates deterministic financial indicators:
    - Current DTI %
    - Proposed EMI
    - Total EMI burden
    - Post-loan DTI %
    - Net disposable surplus
    - Credit utilization %
    """
    # 1. Proposed EMI
    proposed_emi, total_interest, total_repayment = calculate_emi_exact(
        principal=req.loan_amount_required,
        annual_rate_pct=req.expected_interest_rate,
        tenure_months=req.loan_tenure_months
    )

    # 2. DTI calculations
    monthly_inc = max(1.0, req.monthly_income)
    current_dti = round((req.existing_monthly_emi / monthly_inc) * 100.0, 2)
    total_emi_burden = round(req.existing_monthly_emi + proposed_emi, 2)
    post_loan_dti = round((total_emi_burden / monthly_inc) * 100.0, 2)

    # 3. Monthly obligations & surplus
    total_obligations = round(total_emi_burden + req.monthly_expenses, 2)
    disposable_surplus = round(req.monthly_income - total_obligations, 2)

    # 4. Credit utilization
    if req.current_credit_utilization is not None:
        credit_util_pct = round(max(0.0, min(100.0, req.current_credit_utilization)), 2)
    elif req.total_credit_limit > 0:
        credit_util_pct = round(max(0.0, min(100.0, (req.credit_used / req.total_credit_limit) * 100.0)), 2)
    else:
        credit_util_pct = 0.0

    # 5. Loan-to-income multiplier
    annual_income = req.monthly_income * 12.0
    loan_to_income = round(req.loan_amount_required / annual_income, 2) if annual_income > 0 else 0.0

    return FinancialMetrics(
        current_dti_pct=current_dti,
        proposed_emi=proposed_emi,
        total_emi_burden=total_emi_burden,
        post_loan_dti_pct=post_loan_dti,
        total_monthly_obligations=total_obligations,
        net_disposable_surplus=disposable_surplus,
        credit_utilization_pct=credit_util_pct,
        loan_to_income_ratio=loan_to_income,
        total_interest_payable=total_interest,
        total_repayment_amount=total_repayment,
        monthly_income=req.monthly_income,
        loan_amount=req.loan_amount_required,
        tenure_months=req.loan_tenure_months,
        interest_rate=req.expected_interest_rate
    )

def compute_eligibility_score(req: LoanApplicationRequest, metrics: FinancialMetrics) -> Tuple[EligibilityScoreBreakdown, str, List[str]]:
    """
    Computes transparent educational eligibility score out of 1000 points.
    Returns:
    (EligibilityScoreBreakdown, category, deterministic_reasons)
    """
    # Component 1: Credit Score (max 350 pts)
    # Range 300 to 900
    norm_credit = max(0.0, min(1.0, (req.credit_score - 300) / 600.0))
    credit_pts = round(norm_credit * 350.0, 1)
    if req.credit_score >= 750:
        credit_rating = "Excellent"
        credit_expl = f"Bureau score of {req.credit_score} is in the top-tier lending bracket."
    elif req.credit_score >= 700:
        credit_rating = "Good"
        credit_expl = f"Bureau score of {req.credit_score} satisfies conventional bank criteria."
    elif req.credit_score >= 620:
        credit_rating = "Moderate"
        credit_expl = f"Bureau score of {req.credit_score} is fair but may incur higher interest spreads."
    else:
        credit_rating = "Low"
        credit_expl = f"Bureau score of {req.credit_score} is below primary lending benchmarks."

    # Component 2: Post-loan DTI (max 250 pts)
    dti = metrics.post_loan_dti_pct
    if dti <= 30.0:
        dti_pts = 250.0
        dti_rating = "Very Healthy"
        dti_expl = f"Post-loan DTI of {dti}% leaves substantial buffer for living expenses."
    elif dti <= 40.0:
        dti_pts = 210.0
        dti_rating = "Healthy"
        dti_expl = f"Post-loan DTI of {dti}% is within the standard 40% comfort zone."
    elif dti <= 50.0:
        dti_pts = 150.0
        dti_rating = "Moderate"
        dti_expl = f"Post-loan DTI of {dti}% touches common underwriting thresholds (50% FOIR limit)."
    elif dti <= 65.0:
        dti_pts = 75.0
        dti_rating = "Stretched"
        dti_expl = f"Post-loan DTI of {dti}% indicates high repayment strain."
    else:
        dti_pts = 20.0
        dti_rating = "Severe"
        dti_expl = f"Post-loan DTI of {dti}% exceeds prudent debt service capacity."

    # Component 3: Income Stability & Profile (max 150 pts)
    exp = req.employment_experience_years or 2.0
    if req.employment_type == "Salaried":
        base_stability = 95.0
        exp_pts = min(40.0, exp * 8.0)
    elif req.employment_type in ["Self-employed", "Business"]:
        base_stability = 80.0
        exp_pts = min(40.0, exp * 7.0)
    else:
        base_stability = 60.0
        exp_pts = min(30.0, exp * 5.0)

    # Income tier scaling (max 15 bonus)
    inc_bonus = 15.0 if req.monthly_income >= 60000 else (10.0 if req.monthly_income >= 35000 else 5.0)
    stability_pts = round(min(150.0, base_stability + exp_pts + inc_bonus), 1)
    stability_rating = "Strong" if stability_pts >= 120 else ("Moderate" if stability_pts >= 90 else "Developing")
    stability_expl = f"{req.employment_type} with {exp:.1f} years experience."

    # Component 4: Credit Utilization (max 150 pts)
    util = metrics.credit_utilization_pct
    if util <= 20.0:
        util_pts = 150.0
        util_rating = "Optimal"
        util_expl = f"Utilization at {util}% reflects disciplined credit line usage."
    elif util <= 30.0:
        util_pts = 130.0
        util_rating = "Healthy"
        util_expl = f"Utilization at {util}% conforms to the recommended 30% ceiling."
    elif util <= 50.0:
        util_pts = 85.0
        util_rating = "Fair"
        util_expl = f"Utilization at {util}% is moderately elevated."
    elif util <= 75.0:
        util_pts = 45.0
        util_rating = "High"
        util_expl = f"Utilization at {util}% suggests reliance on revolving card debt."
    else:
        util_pts = 15.0
        util_rating = "Critical"
        util_expl = f"Utilization at {util}% is near card capacity, raising risk indicators."

    # Component 5: Disposable Surplus & Affordability (max 100 pts)
    surplus_ratio = (metrics.net_disposable_surplus / req.monthly_income) if req.monthly_income > 0 else 0.0
    if surplus_ratio >= 0.35:
        buffer_pts = 100.0
        buffer_rating = "Generous"
        buffer_expl = f"Net surplus of ₹{metrics.net_disposable_surplus:,.0f} ({surplus_ratio*100:.1f}%) provides strong emergency cushion."
    elif surplus_ratio >= 0.20:
        buffer_pts = 75.0
        buffer_rating = "Adequate"
        buffer_expl = f"Net surplus of ₹{metrics.net_disposable_surplus:,.0f} ({surplus_ratio*100:.1f}%) covers essential living needs."
    elif surplus_ratio >= 0.05:
        buffer_pts = 40.0
        buffer_rating = "Tight"
        buffer_expl = f"Net surplus of ₹{metrics.net_disposable_surplus:,.0f} leaves slim margin for unforeseen expenses."
    elif surplus_ratio >= 0.0:
        buffer_pts = 15.0
        buffer_rating = "Very Tight"
        buffer_expl = "Monthly income barely covers all obligations."
    else:
        buffer_pts = 0.0
        buffer_rating = "Deficit"
        buffer_expl = f"Expenses and EMIs exceed income by ₹{abs(metrics.net_disposable_surplus):,.0f} monthly."

    total_score = int(round(credit_pts + dti_pts + stability_pts + util_pts + buffer_pts))
    total_score = max(100, min(1000, total_score))

    # Determine Category
    if (
        total_score >= 710
        and metrics.post_loan_dti_pct <= 48.0
        and req.credit_score >= 680
        and metrics.net_disposable_surplus > 0
    ):
        category = "Likely Eligible"
    elif (
        total_score >= 540
        and metrics.post_loan_dti_pct <= 65.0
        and req.credit_score >= 600
        and metrics.net_disposable_surplus >= -5000
    ):
        category = "May Require Review"
    else:
        category = "Potentially Difficult"

    # Deterministic reasons based on actual values
    reasons: List[str] = []

    # 1. Credit score reason
    if req.credit_score >= 750:
        reasons.append(f"Your credit score of {req.credit_score} is within a generally favorable range for prime interest rates.")
    elif req.credit_score >= 680:
        reasons.append(f"Your credit score of {req.credit_score} satisfies standard eligibility criteria for most lenders.")
    else:
        reasons.append(f"Your credit score of {req.credit_score} is below primary lending benchmarks (700+), which may restrict lender options.")

    # 2. DTI reason
    if metrics.post_loan_dti_pct <= 35.0:
        reasons.append(f"Your post-loan debt-to-income ratio ({metrics.post_loan_dti_pct}%) represents a very manageable share of your income.")
    elif metrics.post_loan_dti_pct <= 50.0:
        reasons.append(f"Your post-loan DTI of {metrics.post_loan_dti_pct}% is acceptable under standard bank guidelines (<=50% FOIR).")
    else:
        reasons.append(f"Your post-loan DTI of {metrics.post_loan_dti_pct}% exceeds 50%, indicating significant monthly debt burden.")

    # 3. Existing EMI reason
    if req.existing_monthly_emi > 0:
        pct_existing = round((req.existing_monthly_emi / req.monthly_income) * 100.0, 1)
        if pct_existing > 25.0:
            reasons.append(f"Your existing EMI obligations (₹{req.existing_monthly_emi:,.0f} / {pct_existing}%) already claim a notable portion of your income.")
        else:
            reasons.append(f"Your existing EMI commitments (₹{req.existing_monthly_emi:,.0f}) are moderate at {pct_existing}% of monthly income.")

    # 4. Utilization reason
    if metrics.credit_utilization_pct <= 30.0:
        reasons.append(f"Your credit utilization of {metrics.credit_utilization_pct}% remains within the recommended 30% ceiling.")
    else:
        reasons.append(f"Your credit utilization of {metrics.credit_utilization_pct}% is elevated above the 30% standard, which impacts credit scoring.")

    # 5. Disposable surplus reason
    if metrics.net_disposable_surplus <= 0:
        reasons.append(f"Current expenses and proposed EMI exceed monthly earnings, leaving zero financial buffer.")
    elif surplus_ratio >= 0.25:
        reasons.append(f"A net monthly surplus of ₹{metrics.net_disposable_surplus:,.0f} provides a healthy buffer for unexpected expenses.")

    score_breakdown = EligibilityScoreBreakdown(
        total_score=total_score,
        max_score=1000,
        credit_score_component=ScoreComponent(
            name="Credit Bureau Profile",
            points_awarded=credit_pts,
            max_points=350.0,
            rating=credit_rating,
            explanation=credit_expl
        ),
        dti_component=ScoreComponent(
            name="Debt-to-Income Capacity",
            points_awarded=dti_pts,
            max_points=250.0,
            rating=dti_rating,
            explanation=dti_expl
        ),
        income_stability_component=ScoreComponent(
            name="Employment & Income Stability",
            points_awarded=stability_pts,
            max_points=150.0,
            rating=stability_rating,
            explanation=stability_expl
        ),
        credit_utilization_component=ScoreComponent(
            name="Credit Line Discipline",
            points_awarded=util_pts,
            max_points=150.0,
            rating=util_rating,
            explanation=util_expl
        ),
        expense_buffer_component=ScoreComponent(
            name="Disposable Cash Buffer",
            points_awarded=buffer_pts,
            max_points=100.0,
            rating=buffer_rating,
            explanation=buffer_expl
        )
    )

    return score_breakdown, category, reasons

def analyze_credit_profile(req: CreditProfileRequest) -> CreditAnalysisResponse:
    """
    Dedicated credit analysis calculation engine.
    """
    # 1. Utilization
    if req.total_credit_limit > 0:
        util_pct = round(max(0.0, min(100.0, (req.used_credit / req.total_credit_limit) * 100.0)), 2)
    else:
        util_pct = 0.0

    if util_pct <= 20.0:
        util_rating = "Excellent (Under 20%)"
    elif util_pct <= 30.0:
        util_rating = "Good (20%–30%)"
    elif util_pct <= 50.0:
        util_rating = "Moderate (30%–50%)"
    else:
        util_rating = "High / Stretched (>50%)"

    # 2. Debt burden ratio
    monthly_inc = max(1.0, req.monthly_income)
    debt_burden_pct = round((req.existing_monthly_emi / monthly_inc) * 100.0, 2)

    # 3. Reference bands (Commonly used reference range)
    bands = [
        CreditBandInfo(
            range_label="800–900",
            band_name="Excellent",
            min_score=800,
            max_score=900,
            is_user_band=(req.credit_score >= 800),
            description="Premium credit standing. Highest likelihood of rate discounts and rapid approval."
        ),
        CreditBandInfo(
            range_label="740–799",
            band_name="Very Good",
            min_score=740,
            max_score=799,
            is_user_band=(740 <= req.credit_score < 800),
            description="Well above average. Favorable interest offers across commercial banks."
        ),
        CreditBandInfo(
            range_label="670–739",
            band_name="Good",
            min_score=670,
            max_score=739,
            is_user_band=(670 <= req.credit_score < 740),
            description="Commonly considered acceptable by most lenders, though rates may vary."
        ),
        CreditBandInfo(
            range_label="580–669",
            band_name="Fair",
            min_score=580,
            max_score=669,
            is_user_band=(580 <= req.credit_score < 670),
            description="May face tighter terms, higher interest, or collateral requirements."
        ),
        CreditBandInfo(
            range_label="300–579",
            band_name="Needs Attention",
            min_score=300,
            max_score=579,
            is_user_band=(req.credit_score < 580),
            description="High risk profile. Prioritize payment rectifications and balance settlements."
        )
    ]

    user_band = next(b for b in bands if b.is_user_band)

    # 4. Factors
    factors = [
        {
            "factor": "Payment History & Score Tier",
            "status": "Strong" if req.credit_score >= 740 else ("Fair" if req.credit_score >= 670 else "Action Needed"),
            "detail": f"Score {req.credit_score} in '{user_band.band_name}' tier ({user_band.range_label})."
        },
        {
            "factor": "Revolving Credit Utilization",
            "status": "Strong" if util_pct <= 30.0 else ("Fair" if util_pct <= 50.0 else "High Risk"),
            "detail": f"{util_pct}% utilized of ₹{req.total_credit_limit:,.0f} limit."
        },
        {
            "factor": "Existing Debt Obligation",
            "status": "Strong" if debt_burden_pct <= 30.0 else ("Fair" if debt_burden_pct <= 45.0 else "High"),
            "detail": f"Existing EMIs claim {debt_burden_pct}% of monthly income."
        },
        {
            "factor": "Credit Depth & Portfolio Mix",
            "status": "Balanced" if (req.number_of_credit_cards >= 1 and req.number_of_active_loans <= 3) else "Review",
            "detail": f"{req.number_of_credit_cards} card(s) and {req.number_of_active_loans} loan account(s)."
        }
    ]

    # 5. Actionable recommendations
    recs: List[str] = []
    if util_pct > 30.0:
        recs.append(f"Lower your card balance by ₹{max(0.0, req.used_credit - (0.30 * req.total_credit_limit)):,.0f} to pull utilization below 30%.")
    else:
        recs.append("Maintain credit card utilization under 30% across billing cycles.")

    if req.credit_score < 750:
        recs.append("Ensure 100% on-time payment track record; even a 30-day delay severely dents bureau standing.")
        recs.append("Avoid opening multiple fresh loan or card inquiries within short 90-day intervals.")
    else:
        recs.append("Your strong score gives you leverage to negotiate lower processing fees with prospective lenders.")

    if req.number_of_credit_cards > 4:
        recs.append("Avoid closing your oldest credit card as credit age positively impacts score stability.")

    return CreditAnalysisResponse(
        credit_score=req.credit_score,
        credit_utilization_pct=util_pct,
        utilization_rating=util_rating,
        debt_burden_ratio_pct=debt_burden_pct,
        reference_band=user_band,
        all_reference_ranges=bands,
        credit_health_factors=factors,
        actionable_recommendations=recs,
        disclaimer=(
            "Reference tiers represent commonly observed industry bands and do not represent "
            "an official CIBIL/Experian or bank underwriting determination."
        )
    )

def calculate_emi_tool(req: EMIRequest) -> EMIResponse:
    """
    Dedicated EMI calculator endpoint calculation.
    """
    tenure_months = req.tenure_value * 12 if req.tenure_type == "years" else req.tenure_value
    monthly_emi, total_interest, total_payment = calculate_emi_exact(
        principal=req.loan_amount,
        annual_rate_pct=req.interest_rate,
        tenure_months=tenure_months
    )

    if total_payment > 0:
        principal_pct = round((req.loan_amount / total_payment) * 100.0, 1)
        interest_pct = round((total_interest / total_payment) * 100.0, 1)
    else:
        principal_pct = 100.0
        interest_pct = 0.0

    schedule = calculate_amortization_schedule(
        principal=req.loan_amount,
        annual_rate_pct=req.interest_rate,
        tenure_months=tenure_months
    )

    return EMIResponse(
        principal_amount=req.loan_amount,
        annual_interest_rate=req.interest_rate,
        tenure_months=tenure_months,
        monthly_emi=monthly_emi,
        total_interest_payable=total_interest,
        total_repayment=total_payment,
        principal_ratio_pct=principal_pct,
        interest_ratio_pct=interest_pct,
        amortization_schedule=schedule
    )
