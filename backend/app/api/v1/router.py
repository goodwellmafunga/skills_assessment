from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    questions,
    assessments,
    dashboard,
    exports,
    telegram_webhook,
    ws,
)

api_router = APIRouter()
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
api_router.include_router(questions.router, prefix="/questions", tags=["questions"])
api_router.include_router(assessments.router, prefix="/assessments", tags=["assessments"])
api_router.include_router(dashboard.router, prefix="/dashboard", tags=["dashboard"])
api_router.include_router(exports.router, prefix="/exports", tags=["exports"])
api_router.include_router(telegram_webhook.router, prefix="/webhooks/twilio", tags=["twilio"])
api_router.include_router(ws.router, tags=["ws"])
