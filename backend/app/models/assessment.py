from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, Float, ForeignKey, UniqueConstraint, JSON, Boolean, Text
from app.models.base import Base, TimestampMixin


class Assessment(Base, TimestampMixin):
    __tablename__ = "assessments"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int | None] = mapped_column(ForeignKey("users.id", ondelete="SET NULL"), nullable=True)
    respondent_sector: Mapped[str | None] = mapped_column(String(100), nullable=True)
    respondent_category: Mapped[str | None] = mapped_column(String(100), nullable=True)
    submission_token: Mapped[str] = mapped_column(String(64), unique=True, index=True)
    overall_score: Mapped[float] = mapped_column(Float)
    soft_score: Mapped[float] = mapped_column(Float)
    digital_score: Mapped[float] = mapped_column(Float)


class AssessmentAnswer(Base):
    __tablename__ = "assessment_answers"
    __table_args__ = (UniqueConstraint("assessment_id", "question_id", name="uq_assessment_question"),)

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id", ondelete="CASCADE"))
    question_id: Mapped[int] = mapped_column(ForeignKey("questions.id", ondelete="RESTRICT"))
    option_id: Mapped[int] = mapped_column(ForeignKey("question_options.id", ondelete="RESTRICT"))


class Recommendation(Base):
    __tablename__ = "recommendations"

    id: Mapped[int] = mapped_column(primary_key=True)
    assessment_id: Mapped[int] = mapped_column(ForeignKey("assessments.id", ondelete="CASCADE"))
    skill_area: Mapped[str] = mapped_column(String(100))
    priority: Mapped[str] = mapped_column(String(20))
    message: Mapped[str] = mapped_column(Text)


class OutboxEvent(Base, TimestampMixin):
    __tablename__ = "outbox_events"

    id: Mapped[int] = mapped_column(primary_key=True)
    event_type: Mapped[str] = mapped_column(String(50), index=True)
    payload: Mapped[dict] = mapped_column(JSON)
    processed: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
