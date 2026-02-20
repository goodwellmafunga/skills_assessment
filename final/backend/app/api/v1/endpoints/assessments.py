from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession

from app.core.database import get_db
from app.core.deps import get_current_user
from app.models.user import User
from app.schemas.assessment import AssessmentSubmitRequest, AssessmentResultOut
from app.services.assessment_service import submit_assessment

router = APIRouter()


@router.post("/submit", response_model=AssessmentResultOut)
async def submit_assessment_endpoint(
    payload: AssessmentSubmitRequest,
    db: AsyncSession = Depends(get_db),
    user: User | None = Depends(get_current_user),
):
    result = await submit_assessment(
        db=db,
        submission_token=payload.submission_token,
        respondent_sector=payload.respondent_sector,
        respondent_category=payload.respondent_category,
        answers=[a.model_dump() for a in payload.answers],
        user_id=user.id if user else None,
    )
    return result
