from typing import Optional, Literal
from pydantic import BaseModel, Field

class FeedbackRequest(BaseModel):
    tool_name: Literal["loan_eligibility", "credit_analyzer", "emi_calculator", "financial_tips", "general"]
    rating: int = Field(..., ge=1, le=5, description="Star rating from 1 to 5")
    comments: Optional[str] = Field(default="", max_length=500, description="Optional user feedback comments")
    session_id: Optional[str] = None

class FeedbackResponse(BaseModel):
    status: str = "received"
    message: str = "Thank you for your feedback! We appreciate your input."
