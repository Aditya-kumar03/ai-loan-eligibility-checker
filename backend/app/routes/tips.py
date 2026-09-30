from fastapi import APIRouter, HTTPException
from backend.app.models.tips import FinancialTipsRequest, FinancialTipsResponse
from backend.app.services.claude_service import generate_financial_tips
from backend.app.utils.logger import logger

router = APIRouter(prefix="/api/ai", tags=["AI Financial Guidance"])

@router.post("/financial-tips", response_model=FinancialTipsResponse)
async def get_financial_tips(request: FinancialTipsRequest):
    """
    AI Financial Guidance endpoint delivering contextual insights on Indian BFSI topics.
    """
    try:
        response = await generate_financial_tips(request)
        return response
    except Exception as e:
        logger.error(f"Financial tips error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Unable to generate financial tips at this time. Please try again."
        )
