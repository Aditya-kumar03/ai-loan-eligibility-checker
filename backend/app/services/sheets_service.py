import datetime
from typing import Optional
from backend.app.config.settings import settings
from backend.app.models.loan import LoanApplicationRequest, FinancialMetrics
from backend.app.utils.logger import logger

SHEET_HEADERS = [
    "Timestamp",
    "Session ID",
    "Age",
    "Employment Type",
    "Monthly Income",
    "Existing EMI",
    "Monthly Expenses",
    "Loan Amount",
    "Loan Tenure (Months)",
    "Interest Rate (%)",
    "Credit Score",
    "Credit Utilization (%)",
    "Loan Type",
    "Estimated EMI",
    "Post Loan DTI (%)",
    "Eligibility Score",
    "Eligibility Category"
]

def append_loan_record_to_sheets(
    req: LoanApplicationRequest,
    metrics: FinancialMetrics,
    score: int,
    category: str,
    session_id: str
) -> bool:
    """
    Appends an anonymized audit row to configured Google Sheet via Service Account.
    If credentials are not set or network fails, logs safely and returns False without blocking user flow.
    """
    if not settings.is_google_sheets_configured:
        logger.debug("Google Sheets integration not configured. Skipping remote audit sync.")
        return False

    try:
        import gspread
        from google.oauth2.service_account import Credentials

        # Format private key properly if newlines were escaped
        private_key = settings.GOOGLE_PRIVATE_KEY.replace("\\n", "\n")

        creds_dict = {
            "type": "service_account",
            "client_email": settings.GOOGLE_SERVICE_ACCOUNT_EMAIL,
            "private_key": private_key,
            "token_uri": "https://oauth2.googleapis.com/token",
        }

        scopes = [
            "https://spreadsheets.google.com/feeds",
            "https://www.googleapis.com/auth/drive"
        ]

        credentials = Credentials.from_service_account_info(creds_dict, scopes=scopes)
        client = gspread.authorize(credentials)

        sheet = client.open_by_key(settings.GOOGLE_SHEETS_ID).sheet1

        # Check if header exists
        existing_values = sheet.row_values(1)
        if not existing_values:
            sheet.append_row(SHEET_HEADERS)

        timestamp_str = datetime.datetime.now(datetime.timezone.utc).isoformat()

        row_data = [
            timestamp_str,
            session_id,
            req.age,
            req.employment_type,
            req.monthly_income,
            req.existing_monthly_emi,
            req.monthly_expenses,
            req.loan_amount_required,
            req.loan_tenure_months,
            req.expected_interest_rate,
            req.credit_score,
            metrics.credit_utilization_pct,
            req.preferred_loan_type,
            metrics.proposed_emi,
            metrics.post_loan_dti_pct,
            score,
            category
        ]

        sheet.append_row(row_data)
        logger.info(f"Successfully synced session {session_id} to Google Sheet.")
        return True

    except Exception as e:
        logger.warning(f"Google Sheets sync failed: {str(e)}. Proceeding without remote logging.")
        return False
