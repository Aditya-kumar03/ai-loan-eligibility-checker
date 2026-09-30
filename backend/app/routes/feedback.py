from fastapi import APIRouter
from backend.app.models.feedback import FeedbackRequest, FeedbackResponse
from backend.app.utils.logger import logger

router = APIRouter(prefix="/api", tags=["User Feedback"])

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """
    User feedback endpoint for platform improvements.
    """
    logger.info(f"Feedback received for {request.tool_name}: rating={request.rating}/5, session={request.session_id}")
    return FeedbackResponse(
        status="received",
        message="Thank you for your valuable feedback! We use your suggestions to refine our financial models."
    )
