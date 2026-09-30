from .health import router as health_router
from .loan import router as loan_router
from .credit import router as credit_router
from .emi import router as emi_router
from .tips import router as tips_router
from .feedback import router as feedback_router

__all__ = [
    "health_router",
    "loan_router",
    "credit_router",
    "emi_router",
    "tips_router",
    "feedback_router"
]
