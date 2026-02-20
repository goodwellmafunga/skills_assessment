from __future__ import annotations

import re
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy import func, select
from sqlalchemy.exc import IntegrityError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from app.core.database import get_db
from app.core.deps import get_admin_user
from app.models.question import Question, QuestionOption
from app.schemas.question import QuestionCreate, QuestionOut

router = APIRouter()


def _normalize_spaces(value: str) -> str:
    """Trim and collapse repeated whitespace to a single space."""
    return re.sub(r"\s+", " ", value.strip())


@router.get("", response_model=list[QuestionOut])
async def list_questions(
    db: AsyncSession = Depends(get_db),
    active_only: bool = Query(False),
    domain: Optional[str] = Query(None, pattern="^(soft|digital)$"),
    category: Optional[str] = Query(None),
):
    stmt = select(Question).options(selectinload(Question.options))

    if active_only:
        stmt = stmt.where(Question.is_active.is_(True))

    if domain:
        stmt = stmt.where(Question.domain == domain)

    if category:
        norm_category = _normalize_spaces(category)
        stmt = stmt.where(func.lower(func.trim(Question.category)) == norm_category.lower())

    stmt = stmt.order_by(Question.display_order.asc(), Question.id.asc())

    result = await db.execute(stmt)
    questions = result.scalars().unique().all()

    # Ensure options are always in a predictable order for the UI/WhatsApp
    for q in questions:
        if q.options:
            q.options.sort(key=lambda o: (o.score, o.label, o.id))

    return questions


@router.post("", response_model=QuestionOut, status_code=201)
async def create_question(
    payload: QuestionCreate,
    db: AsyncSession = Depends(get_db),
    _admin=Depends(get_admin_user),
):
    if len(payload.options) < 2:
        raise HTTPException(status_code=400, detail="At least two options required")

    # Normalize inputs (helps avoid accidental duplicates)
    norm_text = _normalize_spaces(payload.text)
    norm_category = _normalize_spaces(payload.category)

    # 1) API-level duplicate check (friendly error message)
    dup_stmt = (
        select(Question.id)
        .where(Question.domain == payload.domain)
        .where(func.lower(func.trim(Question.category)) == norm_category.lower())
        .where(func.lower(func.trim(Question.text)) == norm_text.lower())
        .limit(1)
    )
    existing_id = (await db.execute(dup_stmt)).scalar_one_or_none()
    if existing_id:
        raise HTTPException(
            status_code=409,
            detail="Question already exists (same domain/category/text)",
        )

    # 2) Validate option labels are unique and store them uppercase (A/B/C/D/E)
    labels = [op.label.strip().upper() for op in payload.options]
    if len(labels) != len(set(labels)):
        raise HTTPException(status_code=400, detail="Duplicate option labels are not allowed")

    question = Question(
        text=norm_text,
        domain=payload.domain,
        category=norm_category,
        display_order=payload.display_order,
        is_active=payload.is_active,
    )

    for op in payload.options:
        question.options.append(
            QuestionOption(
                label=op.label.strip().upper(),
                text=_normalize_spaces(op.text),
                score=op.score,
            )
        )

    db.add(question)

    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        # In case you add DB constraints later, this remains a safe fallback
        raise HTTPException(status_code=409, detail="Duplicate detected (DB constraint)")

    # Return with options loaded + predictable ordering
    result = await db.execute(
        select(Question)
        .options(selectinload(Question.options))
        .where(Question.id == question.id)
    )
    created = result.scalar_one()
    if created.options:
        created.options.sort(key=lambda o: (o.score, o.label, o.id))
    return created
