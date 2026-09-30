from typing import Optional, List
from pydantic import BaseModel, Field

class CreditProfileRequest(BaseModel):
    credit_score: int = Field(..., ge=300, le=900, description="Bureau credit score between 300 and 900")
    total_credit_limit: float = Field(..., ge=0, description="Total credit limit across credit cards in INR")
    used_credit: float = Field(..., ge=0, description="Total outstanding credit card balance in INR")
    number_of_credit_cards: int = Field(default=1, ge=0, le=30, description="Number of active credit cards")
    number_of_active_loans: int = Field(default=0, ge=0, le=30, description="Number of existing loans")
    monthly_income: float = Field(..., gt=0, description="Monthly net income in INR")
    existing_monthly_emi: float = Field(default=0.0, ge=0, description="Monthly debt payment obligations in INR")

class CreditBandInfo(BaseModel):
    range_label: str
    band_name: str
    min_score: int
    max_score: int
    is_user_band: bool
    description: str

class CreditAnalysisResponse(BaseModel):
    credit_score: int
    credit_utilization_pct: float
    utilization_rating: str
    debt_burden_ratio_pct: float
    reference_band: CreditBandInfo
    all_reference_ranges: List[CreditBandInfo]
    credit_health_factors: List[dict]
    actionable_recommendations: List[str]
    disclaimer: str
