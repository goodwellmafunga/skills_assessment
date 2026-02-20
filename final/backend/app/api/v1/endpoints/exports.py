from fastapi import APIRouter, Depends
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from io import BytesIO
import pandas as pd

from app.core.database import get_db
from app.core.deps import get_admin_user
from app.models.assessment import Assessment, AssessmentAnswer
from app.models.question import Question, QuestionOption

router = APIRouter()


@router.get("/assessments.xlsx")
async def export_assessments_excel(
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    # -------------------------------------------------------
    # 1️⃣ NATIONAL SUMMARY (Completed Assessments Only)
    # -------------------------------------------------------
    summary_q = await db.execute(
        select(
            func.count(Assessment.id),
            func.avg(Assessment.overall_score),
            func.avg(Assessment.soft_score),
            func.avg(Assessment.digital_score),
        )
        .where(Assessment.overall_score > 0)
    )

    total, avg_overall, avg_soft, avg_digital = summary_q.one()

    summary_df = pd.DataFrame([
        {
            "Total Assessments": int(total or 0),
            "Average Overall Score": round(float(avg_overall or 0), 2),
            "Average Soft Skills": round(float(avg_soft or 0), 2),
            "Average Digital Skills": round(float(avg_digital or 0), 2),
        }
    ])

    # -------------------------------------------------------
    # 2️⃣ SKILL GAP ANALYSIS (Lowest Scores First)
    # -------------------------------------------------------
    skill_q = await db.execute(
        select(
            Question.category.label("skill_area"),
            func.avg(QuestionOption.score).label("avg_score"),
            func.count(AssessmentAnswer.id).label("responses"),
        )
        .select_from(AssessmentAnswer)
        .join(QuestionOption, QuestionOption.id == AssessmentAnswer.option_id)
        .join(Question, Question.id == AssessmentAnswer.question_id)
        .group_by(Question.category)
        .order_by(func.avg(QuestionOption.score).asc())
    )

    skill_rows = skill_q.all()

    skill_data = []
    for r in skill_rows:
        avg_score = round(float(r.avg_score or 0), 2)

        if avg_score < 3:
            risk = "High"
        elif avg_score < 3.5:
            risk = "Medium"
        else:
            risk = "Low"

        skill_data.append({
            "Skill Area": r.skill_area,
            "Average Score": avg_score,
            "Risk Level": risk,
            "Total Responses": int(r.responses),
        })

    skill_df = pd.DataFrame(skill_data)

    # -------------------------------------------------------
    # 3️⃣ SECTOR PERFORMANCE
    # -------------------------------------------------------
    sector_q = await db.execute(
        select(
            Assessment.respondent_sector,
            func.avg(Assessment.overall_score),
            func.avg(Assessment.digital_score),
            func.count(Assessment.id),
        )
        .where(Assessment.overall_score > 0)
        .group_by(Assessment.respondent_sector)
    )

    sector_rows = sector_q.all()

    sector_data = [
        {
            "Sector": r[0],
            "Avg Overall Score": round(float(r[1] or 0), 2),
            "Avg Digital Score": round(float(r[2] or 0), 2),
            "Assessments": int(r[3]),
        }
        for r in sector_rows if r[0] is not None
    ]

    sector_df = pd.DataFrame(sector_data)

    # -------------------------------------------------------
    # 4️⃣ RISK DISTRIBUTION (Overall Score)
    # -------------------------------------------------------
    risk_q = await db.execute(
        select(Assessment.overall_score)
        .where(Assessment.overall_score > 0)
    )

    scores = [r[0] for r in risk_q.all()]

    risk_counts = {"High Risk (<3)": 0, "Medium Risk (3–3.5)": 0, "Low Risk (>3.5)": 0}

    for s in scores:
        if s < 3:
            risk_counts["High Risk (<3)"] += 1
        elif s < 3.5:
            risk_counts["Medium Risk (3–3.5)"] += 1
        else:
            risk_counts["Low Risk (>3.5)"] += 1

    risk_df = pd.DataFrame([
        {"Risk Level": k, "Count": v}
        for k, v in risk_counts.items()
    ])

    # -------------------------------------------------------
    # 5️⃣ RAW DATA (Cleaned – Completed Only)
    # -------------------------------------------------------
    rows = await db.execute(
        select(Assessment).where(Assessment.overall_score > 0)
    )
    records = rows.scalars().all()

    raw_data = [
        {
            "Assessment ID": r.id,
            "User ID": r.user_id,
            "Sector": r.respondent_sector,
            "Category": r.respondent_category,
            "Overall Score": r.overall_score,
            "Soft Score": r.soft_score,
            "Digital Score": r.digital_score,
            "Created At": r.created_at.isoformat() if r.created_at else None,
        }
        for r in records
    ]

    raw_df = pd.DataFrame(raw_data)

    # -------------------------------------------------------
    # WRITE MULTI-SHEET EXCEL
    # -------------------------------------------------------
    output = BytesIO()

    with pd.ExcelWriter(output, engine="openpyxl") as writer:
        summary_df.to_excel(writer, index=False, sheet_name="National Summary")
        skill_df.to_excel(writer, index=False, sheet_name="Skill Gaps")
        sector_df.to_excel(writer, index=False, sheet_name="Sector Analysis")
        risk_df.to_excel(writer, index=False, sheet_name="Risk Distribution")
        raw_df.to_excel(writer, index=False, sheet_name="Raw Data")

    output.seek(0)

    return StreamingResponse(
        output,
        media_type="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        headers={"Content-Disposition": "attachment; filename=skills_policy_report.xlsx"},
    )