from typing import List, Literal
from pydantic import BaseModel, Field

class EMIRequest(BaseModel):
    loan_amount: float = Field(..., gt=0, description="Principal loan amount in INR")
    interest_rate: float = Field(..., ge=0.0, le=50.0, description="Annual interest rate in %")
    tenure_value: int = Field(..., gt=0, le=360, description="Tenure value in months or years")
    tenure_type: Literal["months", "years"] = Field(default="years", description="Unit of tenure")

class AmortizationYear(BaseModel):
    year: int
    principal_paid: float
    interest_paid: float
    total_payment_year: float
    remaining_balance: float

class EMIResponse(BaseModel):
    principal_amount: float
    annual_interest_rate: float
    tenure_months: int
    monthly_emi: float
    total_interest_payable: float
    total_repayment: float
    principal_ratio_pct: float
    interest_ratio_pct: float
    amortization_schedule: List[AmortizationYear]
