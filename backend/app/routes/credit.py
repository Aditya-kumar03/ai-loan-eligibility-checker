from fastapi import APIRouter, HTTPException
from backend.app.models.credit import CreditProfileRequest, CreditAnalysisResponse
from backend.app.services.calculator import analyze_credit_profile
from backend.app.utils.logger import logger

router = APIRouter(prefix="/api/credit", tags=["Credit Analyzer"])

@router.post("/analyze", response_model=CreditAnalysisResponse)
async def analyze_credit(request: CreditProfileRequest):
    """
    Dedicated Credit Score & Utilization Analyzer endpoint.
    """
    try:
        response = analyze_credit_profile(request)
        return response
    except ValueError as ve:
        logger.warning(f"Credit analyzer validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Credit analyzer error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while analyzing your credit profile. Please try again."
        )
