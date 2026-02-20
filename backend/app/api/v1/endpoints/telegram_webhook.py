import uuid
import httpx
from fastapi import APIRouter, Request, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from sqlalchemy.orm import selectinload

from app.core.config import settings
from app.core.database import get_db
from app.models.question import Question, QuestionOption
from app.models.assessment import Assessment, AssessmentAnswer, Recommendation
from app.models.chat_session import ChatSession

router = APIRouter()

TELEGRAM_API = f"https://api.telegram.org/bot{settings.TELEGRAM_BOT_TOKEN}"


# --------------------------
# Utility Functions
# --------------------------

def parse_choice(msg: str) -> str | None:
    if not msg:
        return None
    s = msg.strip().lower()
    ch = s[0]
    return ch if ch in {"a", "b", "c", "d", "e"} else None


def normalize_cmd(text: str) -> str:
    """
    Accepts: reset, RESET, [RESET], (reset), /reset
    Also accepts: ready, READY, [READY], (ready), /ready
    """
    if not text:
        return ""
    s = text.strip().lower()
    # remove common wrappers
    if s.startswith("/") and len(s) > 1:
        s = s[1:]
    if (s.startswith("[") and s.endswith("]")) or (s.startswith("(") and s.endswith(")")):
        s = s[1:-1].strip()
    return s


async def get_first_question(db: AsyncSession) -> Question | None:
    res = await db.execute(
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.is_active.is_(True))
        .order_by(Question.display_order.asc(), Question.id.asc())
        .limit(1)
    )
    return res.scalar_one_or_none()


async def get_next_question(db: AsyncSession, current: Question) -> Question | None:
    res = await db.execute(
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.is_active.is_(True))
        .where(
            (Question.display_order > current.display_order)
            | ((Question.display_order == current.display_order) & (Question.id > current.id))
        )
        .order_by(Question.display_order.asc(), Question.id.asc())
        .limit(1)
    )
    return res.scalar_one_or_none()


def format_question(q: Question, total: int | None = None) -> str:
    header = f"Q{q.display_order}"
    if total:
        header = f"{header}/{total}"

    lines = [
        f"{header} ({q.domain.capitalize()} - {q.category})",
        q.text.strip(),
        ""
    ]

    opts = sorted(q.options or [], key=lambda o: (o.label or ""))
    for op in opts:
        lines.append(f"{op.label.upper()}) {op.text.strip()}")

    lines.append("")
    lines.append("Reply with A, B, C, D, or E.")
    lines.append("Type (reset) or [RESET] anytime to restart.")
    return "\n".join(lines)


async def count_active_questions(db: AsyncSession) -> int:
    res = await db.execute(
        select(func.count()).select_from(Question).where(Question.is_active.is_(True))
    )
    return int(res.scalar_one())


async def get_active_session(db: AsyncSession, user_id: str) -> ChatSession | None:
    res = await db.execute(
        select(ChatSession)
        .where(ChatSession.channel == "telegram")
        .where(ChatSession.phone == user_id)
        .where(ChatSession.state == "in_progress")
        .order_by(ChatSession.id.desc())
        .limit(1)
    )
    return res.scalar_one_or_none()


async def get_any_session(db: AsyncSession, user_id: str) -> ChatSession | None:
    """
    Because you have UNIQUE(channel, phone), there is at most 1 row anyway,
    but we keep this generic in case your schema changes later.
    """
    res = await db.execute(
        select(ChatSession)
        .where(ChatSession.channel == "telegram")
        .where(ChatSession.phone == user_id)
        .order_by(ChatSession.id.desc())
        .limit(1)
    )
    return res.scalar_one_or_none()


async def compute_scores(db: AsyncSession, assessment_id: int) -> tuple[float, float, float]:
    rows = (
        await db.execute(
            select(Question.domain, func.avg(QuestionOption.score))
            .select_from(AssessmentAnswer)
            .join(QuestionOption, QuestionOption.id == AssessmentAnswer.option_id)
            .join(Question, Question.id == AssessmentAnswer.question_id)
            .where(AssessmentAnswer.assessment_id == assessment_id)
            .group_by(Question.domain)
        )
    ).all()

    soft_avg = 0.0
    digital_avg = 0.0

    for domain, avg_score in rows:
        if domain == "soft":
            soft_avg = float(avg_score or 0.0)
        elif domain == "digital":
            digital_avg = float(avg_score or 0.0)

    total_avg = (soft_avg + digital_avg) / (
        2 if (soft_avg and digital_avg)
        else 1 if (soft_avg or digital_avg)
        else 1
    )
    return soft_avg, digital_avg, total_avg


def recommendation_for(domain: str, avg: float) -> tuple[str, str]:
    if avg >= 4.0:
        return ("Low", f"Great {domain} skills. Maintain consistency and try advanced practice tasks.")
    if avg >= 3.0:
        return ("Medium", f"Good {domain} skills. Improve through weekly practice and feedback.")
    return ("High", f"{domain.capitalize()} skills need attention. Start with basics + structured training plan.")


# --------------------------
# Telegram Webhook
# --------------------------

@router.post("/telegram")
async def telegram_webhook(request: Request, db: AsyncSession = Depends(get_db)):

    update = await request.json()

    if "message" not in update:
        return {"ok": True}

    message = update["message"]
    incoming = (message.get("text") or "").strip()
    user_id = str(message["from"]["id"])
    cmd = normalize_cmd(incoming)

    async def send_reply(text: str):
        async with httpx.AsyncClient(timeout=15) as client:
            await client.post(
                f"{TELEGRAM_API}/sendMessage",
                json={"chat_id": user_id, "text": text}
            )

    # --------------------------
    # Greeting
    # --------------------------
    if cmd in {"hi", "hello", "start"}:
        await send_reply(
            "Welcome to Skills Assessment ✅\n"
            "Reply READY to begin.\n"
            "To restart at any time type: (reset) or [RESET]"
        )
        return {"ok": True}

    # --------------------------
    # RESET (accept: reset, (reset), [RESET], /reset)
    # --------------------------
    if cmd == "reset":
        s = await get_any_session(db, user_id)
        if s:
            s.state = "cancelled"
            s.current_question_id = None
            await db.commit()

        await send_reply("Session reset ✅\nReply READY to begin again.")
        return {"ok": True}

    # --------------------------
    # READY
    # --------------------------
    if cmd == "ready":

        first_q = await get_first_question(db)
        if not first_q:
            await send_reply("No active questions found in the system.")
            return {"ok": True}

        # If active session exists, continue
        existing_session = await get_active_session(db, user_id)
        if existing_session:
            qres = await db.execute(
                select(Question)
                .options(selectinload(Question.options))
                .where(Question.id == existing_session.current_question_id)
            )
            current_q = qres.scalar_one_or_none()
            total = await count_active_questions(db)
            await send_reply(format_question(current_q, total=total))
            return {"ok": True}

        # Otherwise create a new assessment but REUSE chat_sessions row to avoid UNIQUE violation
        assessment = Assessment(
            submission_token=uuid.uuid4().hex,
            overall_score=0.0,
            soft_score=0.0,
            digital_score=0.0,
        )
        db.add(assessment)
        await db.flush()

        existing_row = await get_any_session(db, user_id)

        if existing_row:
            # ✅ reuse existing chat session row
            existing_row.state = "in_progress"
            existing_row.assessment_id = assessment.id
            existing_row.current_question_id = first_q.id
            await db.commit()
        else:
            # first time user
            session = ChatSession(
                channel="telegram",
                phone=user_id,
                state="in_progress",
                assessment_id=assessment.id,
                current_question_id=first_q.id,
            )
            db.add(session)
            await db.commit()

        total = await count_active_questions(db)
        await send_reply(format_question(first_q, total=total))
        return {"ok": True}

    # --------------------------
    # Answer Flow
    # --------------------------
    session = await get_active_session(db, user_id)

    if not session:
        await send_reply("No active session found. Reply READY to begin.\nTip: type (reset) if you are stuck.")
        return {"ok": True}

    choice = parse_choice(incoming)

    if not choice:
        await send_reply("Please reply with A, B, C, D, or E.\n(Or type (reset) / [RESET] to restart.)")
        return {"ok": True}

    qres = await db.execute(
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.id == session.current_question_id)
    )
    current_q = qres.scalar_one_or_none()

    if not current_q:
        session.state = "cancelled"
        await db.commit()
        await send_reply("Session error. Reply READY to begin again.\nTip: type (reset) if it persists.")
        return {"ok": True}

    option = next(
        (o for o in (current_q.options or []) if (o.label or "").lower() == choice),
        None
    )

    if not option:
        await send_reply("Invalid choice. Reply A, B, C, D, or E.\nType (reset) to restart.")
        return {"ok": True}

    existing = (
        await db.execute(
            select(AssessmentAnswer)
            .where(AssessmentAnswer.assessment_id == session.assessment_id)
            .where(AssessmentAnswer.question_id == current_q.id)
            .limit(1)
        )
    ).scalar_one_or_none()

    if existing:
        existing.option_id = option.id
    else:
        db.add(
            AssessmentAnswer(
                assessment_id=session.assessment_id,
                question_id=current_q.id,
                option_id=option.id,
            )
        )

    next_q = await get_next_question(db, current_q)

    if next_q:
        session.current_question_id = next_q.id
        await db.commit()
        total = await count_active_questions(db)
        await send_reply(format_question(next_q, total=total))
        return {"ok": True}

    # --------------------------
    # Completed
    # --------------------------
    soft_avg, digital_avg, overall_avg = await compute_scores(db, session.assessment_id)

    a = (await db.execute(
        select(Assessment).where(Assessment.id == session.assessment_id)
    )).scalar_one()

    a.soft_score = soft_avg
    a.digital_score = digital_avg
    a.overall_score = overall_avg

    pr, msg = recommendation_for("soft", soft_avg)
    db.add(Recommendation(assessment_id=a.id, skill_area="soft", priority=pr, message=msg))

    pr, msg = recommendation_for("digital", digital_avg)
    db.add(Recommendation(assessment_id=a.id, skill_area="digital", priority=pr, message=msg))

    session.state = "completed"
    await db.commit()

    await send_reply(
        "Assessment completed ✅\n"
        f"Soft: {soft_avg:.2f}/5\n"
        f"Digital: {digital_avg:.2f}/5\n"
        f"Overall: {overall_avg:.2f}/5\n\n"
        "To do the assessment again, type: (reset) or [RESET], then READY."
    )

    return {"ok": True}