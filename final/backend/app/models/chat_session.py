from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy import String, ForeignKey, Integer
from app.models.base import Base, TimestampMixin


class ChatSession(Base, TimestampMixin):
    """
    Stores WhatsApp (or future SMS) conversation state:
    - which assessment is in progress
    - which question user is currently answering
    """
    __tablename__ = "chat_sessions"

    id: Mapped[int] = mapped_column(primary_key=True)

    channel: Mapped[str] = mapped_column(
        String(20),
        default="whatsapp",
        index=True
    )

    # 🔥 FIXED (was from_number)
    phone: Mapped[str] = mapped_column(
        String(40),
        index=True
    )

    # 🔥 FIXED (was status)
    state: Mapped[str] = mapped_column(
        String(20),
        default="in_progress",
        index=True
    )

    assessment_id: Mapped[int] = mapped_column(
        ForeignKey("assessments.id", ondelete="CASCADE")
    )

    current_question_id: Mapped[int | None] = mapped_column(
        ForeignKey("questions.id", ondelete="SET NULL"),
        nullable=True,
    )
