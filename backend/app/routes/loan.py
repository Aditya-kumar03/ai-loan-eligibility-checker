import uuid
from fastapi import APIRouter, HTTPException, BackgroundTasks
from backend.app.models.loan import LoanApplicationRequest, LoanApplicationResponse
from backend.app.services.calculator import (
    compute_financial_metrics,
    compute_eligibility_score,
    DISCLAIMER_TEXT
)
from backend.app.services.claude_service import analyze_loan_with_claude
from backend.app.services.sheets_service import append_loan_record_to_sheets
from backend.app.utils.logger import logger

router = APIRouter(prefix="/api/loan", tags=["Loan Eligibility"])

@router.post("/analyze", response_model=LoanApplicationResponse)
async def analyze_loan_application(
    request: LoanApplicationRequest,
    background_tasks: BackgroundTasks
):
    """
    Main loan underwriting analysis endpoint.
    1. Validates input
    2. Runs deterministic financial mathematics (EMI, DTI, FOIR, credit utilization)
    3. Computes internal Educational Eligibility Score & Breakdown
    4. Triggers Claude AI for contextual explanations (or transparent deterministic fallback)
    5. Dispatches background audit sync to Google Sheets (if configured)
    """
    try:
        session_id = request.session_id or f"SES-{uuid.uuid4().hex[:8].upper()}"

        # 1. Deterministic Metrics
        metrics = compute_financial_metrics(request)

        # 2. Eligibility Score & Breakdown
        score_breakdown, category, reasons = compute_eligibility_score(request, metrics)

        # 3. AI Analysis (with automatic fallback)
        ai_analysis = await analyze_loan_with_claude(
            req=request,
            metrics=metrics,
            category=category,
            score=score_breakdown.total_score
        )

        # 4. Schedule Google Sheets sync in background
        background_tasks.add_task(
            append_loan_record_to_sheets,
            req=request,
            metrics=metrics,
            score=score_breakdown.total_score,
            category=category,
            session_id=session_id
        )

        return LoanApplicationResponse(
            session_id=session_id,
            status="success",
            eligibility_category=category,
            estimated_eligibility_score=score_breakdown.total_score,
            score_breakdown=score_breakdown,
            metrics=metrics,
            deterministic_reasons=reasons,
            ai_analysis=ai_analysis,
            disclaimer=DISCLAIMER_TEXT,
            sheets_synced=False # Updated asynchronously
        )

    except ValueError as ve:
        logger.warning(f"Validation error in loan analysis: {str(ve)}")
        raise HTTPException(status_code=400, detail=str(ve))
    except Exception as e:
        logger.error(f"Internal server error in loan analysis: {str(e)}", exc_info=True)
        raise HTTPException(
            status_code=500,
            detail="Something went wrong while analyzing your request. Please check your inputs and try again."
        )
