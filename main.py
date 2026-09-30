"""
AI Loan Eligibility Checker - Root Application Entrypoint
Allows running directly from project root with:
    py main.py
or
    uvicorn main:app --reload
"""
from backend.main import app

if __name__ == "__main__":
    import uvicorn
    from backend.app.config.settings import settings
    uvicorn.run("backend.main:app", host=settings.HOST, port=settings.PORT, reload=True)
