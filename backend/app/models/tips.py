from typing import Optional, List, Literal
from pydantic import BaseModel, Field

TopicType = Literal[
    "Credit Score",
    "Loans",
    "EMI Management",
    "Budgeting",
    "Debt Management",
    "Savings",
    "Financial Planning"
]

class FinancialTipsRequest(BaseModel):
    topic: TopicType = Field(..., description="Financial topic category")
    user_context: Optional[str] = Field(
        default="", max_length=300, description="Optional brief context e.g. 'Salaried, planning home loan'"
    )

class TipItem(BaseModel):
    title: str
    content: str
    impact_level: Literal["High", "Medium", "Fundamental"]
    action_item: str

class FinancialTipsResponse(BaseModel):
    topic: str
    overview: str
    tips: List[TipItem]
    pro_tip: str
    is_ai_generated: bool
    notice: Optional[str] = None
    disclaimer: str
