import datetime
from fastapi import APIRouter
from backend.app.config.settings import settings

router = APIRouter(prefix="/api", tags=["System"])

@router.get("/health")
async def health_check():
    """
    Returns system status, service health, and configuration flags.
    """
    return {
        "status": "healthy",
        "service": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "environment": settings.ENVIRONMENT,
        "integrations": {
            "claude_ai": {
                "configured": settings.is_claude_configured,
                "model": settings.CLAUDE_MODEL if settings.is_claude_configured else None,
                "mode": "Active" if settings.is_claude_configured else "Rule-Engine Fallback"
            },
            "google_sheets": {
                "configured": settings.is_google_sheets_configured,
                "mode": "Active" if settings.is_google_sheets_configured else "Local Only"
            }
        },
        "timestamp_utc": datetime.datetime.now(datetime.timezone.utc).isoformat()
    }
