import pytest
from backend.app.config.settings import settings
from backend.app.services.claude_service import (
    generate_deterministic_loan_ai_fallback,
    analyze_loan_with_claude,
    generate_financial_tips,
    FALLBACK_NOTICE
)
from backend.app.models.loan import LoanApplicationRequest
from backend.app.models.tips import FinancialTipsRequest
from backend.app.services.calculator import compute_financial_metrics

@pytest.mark.asyncio
async def test_loan_ai_fallback_when_unconfigured():
    # Ensure CLAUDE_API_KEY is empty for this test
    original_key = settings.CLAUDE_API_KEY
    settings.CLAUDE_API_KEY = ""

    try:
        req = LoanApplicationRequest(
            age=29,
            employment_type="Salaried",
            monthly_income=80000,
            existing_monthly_emi=10000,
            monthly_expenses=20000,
            loan_amount_required=600000,
            loan_tenure_months=60,
            expected_interest_rate=11.5,
            credit_score=750,
            total_credit_limit=250000,
            credit_used=50000
        )
        metrics = compute_financial_metrics(req)

        result = await analyze_loan_with_claude(
            req=req,
            metrics=metrics,
            category="Likely Eligible",
            score=760
        )

        assert result.is_ai_generated is False
        assert result.notice == FALLBACK_NOTICE
        assert len(result.strengths) > 0
        assert len(result.recommendations) > 0
        assert len(result.questions_for_lender) > 0
        assert "760" in result.summary
    finally:
        settings.CLAUDE_API_KEY = original_key

@pytest.mark.asyncio
async def test_financial_tips_fallback():
    original_key = settings.CLAUDE_API_KEY
    settings.CLAUDE_API_KEY = ""

    try:
        req = FinancialTipsRequest(topic="EMI Management")
        result = await generate_financial_tips(req)

        assert result.is_ai_generated is False
        assert result.notice == FALLBACK_NOTICE
        assert len(result.tips) >= 3
        assert result.topic == "EMI Management"
    finally:
        settings.CLAUDE_API_KEY = original_key
