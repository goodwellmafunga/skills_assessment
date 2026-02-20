from collections import defaultdict
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from fastapi import HTTPException

from app.models.question import Question, QuestionOption
from app.models.assessment import Assessment, AssessmentAnswer, Recommendation, OutboxEvent
from app.services.recommendation_service import generate_recommendations


async def submit_assessment(
    db: AsyncSession,
    submission_token: str,
    respondent_sector: str | None,
    respondent_category: str | None,
    answers: list[dict],
    user_id: int | None = None,
) -> dict:
    # Idempotency guard
    existing = await db.execute(select(Assessment).where(Assessment.submission_token == submission_token))
    found = existing.scalar_one_or_none()
    if found:
        raise HTTPException(status_code=409, detail="Duplicate submission token")

    # Fetch all active questions and options for validation
    q_rows = await db.execute(select(Question).where(Question.is_active.is_(True)))
    questions = {q.id: q for q in q_rows.scalars().all()}

    opt_rows = await db.execute(select(QuestionOption))
    options = {o.id: o for o in opt_rows.scalars().all()}

    if not answers:
        raise HTTPException(status_code=400, detail="No answers provided")

    total_score = 0
    count = 0
    domain_score = defaultdict(list)
    category_score = defaultdict(list)

    # atomic transaction boundary (ACID)
    async with db.begin():
        assessment = Assessment(
            user_id=user_id,
            respondent_sector=respondent_sector,
            respondent_category=respondent_category,
            submission_token=submission_token,
            overall_score=0,
            soft_score=0,
            digital_score=0,
        )
        db.add(assessment)
        await db.flush()

        for ans in answers:
            qid = ans["question_id"]
            oid = ans["option_id"]

            q = questions.get(qid)
            opt = options.get(oid)
            if not q or not opt or opt.question_id != qid:
                raise HTTPException(status_code=400, detail=f"Invalid answer mapping question={qid} option={oid}")

            db.add(AssessmentAnswer(
                assessment_id=assessment.id,
                question_id=qid,
                option_id=oid,
            ))

            score = opt.score
            total_score += score
            count += 1
            domain_score[q.domain].append(score)
            category_score[q.category].append(score)

        overall = round(total_score / max(count, 1), 2)
        soft = round(sum(domain_score["soft"]) / max(len(domain_score["soft"]), 1), 2) if domain_score["soft"] else 0.0
        digital = round(sum(domain_score["digital"]) / max(len(domain_score["digital"]), 1), 2) if domain_score["digital"] else 0.0

        assessment.overall_score = overall
        assessment.soft_score = soft
        assessment.digital_score = digital

        cat_avg = {k: round(sum(v)/len(v), 2) for k, v in category_score.items() if v}
        recs = generate_recommendations(cat_avg)

        for r in recs:
            db.add(Recommendation(
                assessment_id=assessment.id,
                skill_area=r["skill_area"],
                priority=r["priority"],
                message=r["message"],
            ))

        # outbox event so UI can update in near-real time
        db.add(OutboxEvent(
            event_type="assessment_submitted",
            payload={
                "assessment_id": assessment.id,
                "overall_score": overall,
                "soft_score": soft,
                "digital_score": digital,
                "respondent_sector": respondent_sector,
                "respondent_category": respondent_category,
            }
        ))

    return {
        "assessment_id": assessment.id,
        "overall_score": overall,
        "soft_score": soft,
        "digital_score": digital,
        "recommendations": recs,
    }
