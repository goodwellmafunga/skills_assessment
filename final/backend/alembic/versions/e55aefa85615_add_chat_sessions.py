"""add chat_sessions

Revision ID: e55aefa85615
Revises: 0001_initial
Create Date: 2026-02-19

"""

from alembic import op
import sqlalchemy as sa


# revision identifiers, used by Alembic.
revision = "e55aefa85615"
down_revision = "0001_initial"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "chat_sessions",
        sa.Column("id", sa.Integer(), primary_key=True),

        sa.Column("channel", sa.String(length=30), nullable=False, server_default="whatsapp"),
        sa.Column("phone", sa.String(length=40), nullable=False),

        sa.Column("state", sa.String(length=30), nullable=False, server_default="new"),
        sa.Column("current_question_id", sa.Integer(), nullable=True),
        sa.Column("assessment_id", sa.Integer(), nullable=True),

        sa.Column("context", sa.JSON(), nullable=False, server_default=sa.text("'{}'::jsonb")),

        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),

        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False, server_default=sa.text("now()")),
        sa.Column("last_message_at", sa.DateTime(timezone=True), nullable=True),

        sa.ForeignKeyConstraint(["current_question_id"], ["questions.id"], ondelete="SET NULL"),
        sa.ForeignKeyConstraint(["assessment_id"], ["assessments.id"], ondelete="SET NULL"),
    )

    op.create_index("ix_chat_sessions_phone", "chat_sessions", ["phone"])
    op.create_index("ix_chat_sessions_state", "chat_sessions", ["state"])
    op.create_unique_constraint(
        "uq_chat_sessions_channel_phone",
        "chat_sessions",
        ["channel", "phone"],
    )


def downgrade() -> None:
    op.drop_constraint("uq_chat_sessions_channel_phone", "chat_sessions", type_="unique")
    op.drop_index("ix_chat_sessions_state", table_name="chat_sessions")
    op.drop_index("ix_chat_sessions_phone", table_name="chat_sessions")
    op.drop_table("chat_sessions")
