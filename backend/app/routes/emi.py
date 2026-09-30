from fastapi import APIRouter, HTTPException
from backend.app.models.emi import EMIRequest, EMIResponse
from backend.app.services.calculator import calculate_emi_tool
from backend.app.utils.logger import logger

router = APIRouter(prefix="/api/emi", tags=["EMI Calculator"])

@router.post("/calculate", response_model=EMIResponse)
async def calculate_emi(request: EMIRequest):
    """
    Dedicated EMI calculation endpoint with amortization breakdown.
    """
    try:
        response = calculate_emi_tool(request)
        return response
    except ValueError as ve:
        logger.warning(f"EMI calculation validation error: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"EMI calculation error: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while calculating the EMI. Please check your inputs and try again."
        )
