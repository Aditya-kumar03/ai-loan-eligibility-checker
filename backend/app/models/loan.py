from typing import Optional, List, Literal
from pydantic import BaseModel, Field, field_validator

class LoanApplicationRequest(BaseModel):
    # Personal Info
    age: int = Field(..., ge=18, le=75, description="Borrower age between 18 and 75")
    employment_type: Literal["Salaried", "Self-employed", "Business", "Other"] = Field(
        ..., description="Employment category"
    )
    employment_experience_years: Optional[float] = Field(
        default=3.0, ge=0, le=60, description="Work or business experience in years"
    )
    existing_bank_relationship: Optional[str] = Field(
        default="Savings Account", description="Prior relationship with a lender"
    )
    preferred_loan_type: Literal[
        "Personal Loan", "Home Loan", "Education Loan", "Vehicle Loan", "Business Loan"
    ] = Field(default="Personal Loan", description="Type of loan requested")

    # Financial Info
    monthly_income: float = Field(..., gt=0, description="Monthly net in-hand income in INR")
    existing_monthly_emi: float = Field(default=0.0, ge=0, description="Existing ongoing monthly EMIs in INR")
    monthly_expenses: float = Field(default=0.0, ge=0, description="Living and recurring monthly expenses in INR")
    loan_amount_required: float = Field(..., gt=0, description="Principal loan requested in INR")
    loan_tenure_months: int = Field(..., gt=0, le=360, description="Tenure in months (1-360)")
    expected_interest_rate: float = Field(..., ge=0.0, le=50.0, description="Annual interest rate in % (e.g. 10.5)")

    # Credit Profile
    credit_score: int = Field(..., ge=300, le=900, description="Credit Bureau Score (300 to 900)")
    total_credit_limit: float = Field(default=0.0, ge=0, description="Total credit limit across credit cards in INR")
    credit_used: float = Field(default=0.0, ge=0, description="Current total used credit in INR")
    current_credit_utilization: Optional[float] = Field(
        default=None, ge=0, le=100, description="Explicit credit utilization % if already calculated"
    )
    number_of_existing_loans: int = Field(default=0, ge=0, le=30, description="Active loans count")
    number_of_credit_cards: int = Field(default=0, ge=0, le=30, description="Active credit cards count")

    session_id: Optional[str] = Field(default=None, description="Optional client session identifier")

    @field_validator("loan_amount_required")
    @classmethod
    def validate_loan_amount(cls, v: float) -> float:
        if v <= 0:
            raise ValueError("Loan amount required must be greater than zero.")
        return v

class FinancialMetrics(BaseModel):
    current_dti_pct: float
    proposed_emi: float
    total_emi_burden: float
    post_loan_dti_pct: float
    total_monthly_obligations: float
    net_disposable_surplus: float
    credit_utilization_pct: float
    loan_to_income_ratio: float
    total_interest_payable: float
    total_repayment_amount: float
    monthly_income: float
    loan_amount: float
    tenure_months: int
    interest_rate: float

class ScoreComponent(BaseModel):
    name: str
    points_awarded: float
    max_points: float
    rating: str
    explanation: str

class EligibilityScoreBreakdown(BaseModel):
    total_score: int
    max_score: int = 1000
    credit_score_component: ScoreComponent
    dti_component: ScoreComponent
    income_stability_component: ScoreComponent
    credit_utilization_component: ScoreComponent
    expense_buffer_component: ScoreComponent

class AIAnalysisResult(BaseModel):
    summary: str
    eligibility_explanation: str
    strengths: List[str]
    concerns: List[str]
    recommendations: List[str]
    risk_considerations: List[str]
    questions_for_lender: List[str]
    is_ai_generated: bool = False
    model_used: str = "Deterministic Rule-Engine Fallback"
    notice: Optional[str] = None

class LoanApplicationResponse(BaseModel):
    session_id: str
    status: str = "success"
    eligibility_category: Literal["Likely Eligible", "May Require Review", "Potentially Difficult"]
    estimated_eligibility_score: int
    score_breakdown: EligibilityScoreBreakdown
    metrics: FinancialMetrics
    deterministic_reasons: List[str]
    ai_analysis: AIAnalysisResult
    disclaimer: str
    sheets_synced: bool = False
