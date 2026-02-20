from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func

from app.core.database import get_db
from app.core.deps import get_admin_user
from app.models.assessment import Assessment
from app.models.assessment import AssessmentAnswer
from app.models.question import Question, QuestionOption
from app.schemas.dashboard import DashboardSummary

router = APIRouter()


@router.get("/summary", response_model=DashboardSummary)
async def dashboard_summary(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    totals = await db.execute(
        select(
            func.count(Assessment.id),
            func.coalesce(func.avg(Assessment.overall_score), 0),
            func.coalesce(func.avg(Assessment.soft_score), 0),
            func.coalesce(func.avg(Assessment.digital_score), 0),
        )
    )
    count, avg_overall, avg_soft, avg_digital = totals.one()

    # ✅ Option A: Lowest scoring skill areas (based on answers + option score)
    # Choose ONE dimension for "skill_area":
    #   - Question.category  (recommended)
    #   - Question.domain
    #   - Question.text (not recommended)
    skill_field = Question.category  # <-- change to Question.skill_area if you have it

    gaps_q = await db.execute(
        select(
            skill_field.label("skill_area"),
            func.coalesce(func.avg(QuestionOption.score), 0).label("avg_score"),
            func.count(AssessmentAnswer.id).label("n_answers"),
        )
        .select_from(AssessmentAnswer)
        .join(QuestionOption, QuestionOption.id == AssessmentAnswer.option_id)
        .join(Question, Question.id == AssessmentAnswer.question_id)
        .group_by(skill_field)
        .order_by(func.avg(QuestionOption.score).asc())  # lowest first
        .limit(10)
    )

    gaps_rows = gaps_q.all()

    return {
        "total_assessments": int(count or 0),
        "avg_overall": round(float(avg_overall or 0), 2),
        "avg_soft": round(float(avg_soft or 0), 2),
        "avg_digital": round(float(avg_digital or 0), 2),

        # Rename top_gaps items to return avg_score
        "top_gaps": [
            {
                "skill_area": r.skill_area,
                "avg_score": round(float(r.avg_score or 0), 2),
                "n_answers": int(r.n_answers or 0),
            }
            for r in gaps_rows
            if r.skill_area is not None
        ],
    }