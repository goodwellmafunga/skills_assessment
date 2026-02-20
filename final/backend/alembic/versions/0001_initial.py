"""initial

Revision ID: 0001_initial
Revises:
Create Date: 2026-02-18
"""

from alembic import op
import sqlalchemy as sa

revision = '0001_initial'
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        'users',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('email', sa.String(255), nullable=False, unique=True),
        sa.Column('full_name', sa.String(255), nullable=False),
        sa.Column('password_hash', sa.String(255), nullable=False),
        sa.Column('is_admin', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('totp_secret', sa.String(64), nullable=True),
        sa.Column('totp_enabled', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'questions',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('domain', sa.String(20), nullable=False),
        sa.Column('category', sa.String(100), nullable=False),
        sa.Column('is_active', sa.Boolean(), nullable=False, server_default=sa.true()),
        sa.Column('display_order', sa.Integer(), nullable=False, server_default='0'),
    )

    op.create_table(
        'question_options',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('question_id', sa.Integer(), sa.ForeignKey('questions.id', ondelete='CASCADE'), nullable=False),
        sa.Column('label', sa.String(10), nullable=False),
        sa.Column('text', sa.Text(), nullable=False),
        sa.Column('score', sa.Integer(), nullable=False),
        sa.CheckConstraint('score >= 1 AND score <= 5', name='ck_score_1_5')
    )

    op.create_table(
        'assessments',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('user_id', sa.Integer(), sa.ForeignKey('users.id', ondelete='SET NULL'), nullable=True),
        sa.Column('respondent_sector', sa.String(100), nullable=True),
        sa.Column('respondent_category', sa.String(100), nullable=True),
        sa.Column('submission_token', sa.String(64), nullable=False, unique=True),
        sa.Column('overall_score', sa.Float(), nullable=False),
        sa.Column('soft_score', sa.Float(), nullable=False),
        sa.Column('digital_score', sa.Float(), nullable=False),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )

    op.create_table(
        'assessment_answers',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('assessment_id', sa.Integer(), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('question_id', sa.Integer(), sa.ForeignKey('questions.id', ondelete='RESTRICT'), nullable=False),
        sa.Column('option_id', sa.Integer(), sa.ForeignKey('question_options.id', ondelete='RESTRICT'), nullable=False),
        sa.UniqueConstraint('assessment_id', 'question_id', name='uq_assessment_question')
    )

    op.create_table(
        'recommendations',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('assessment_id', sa.Integer(), sa.ForeignKey('assessments.id', ondelete='CASCADE'), nullable=False),
        sa.Column('skill_area', sa.String(100), nullable=False),
        sa.Column('priority', sa.String(20), nullable=False),
        sa.Column('message', sa.Text(), nullable=False),
    )

    op.create_table(
        'outbox_events',
        sa.Column('id', sa.Integer(), primary_key=True),
        sa.Column('event_type', sa.String(50), nullable=False),
        sa.Column('payload', sa.JSON(), nullable=False),
        sa.Column('processed', sa.Boolean(), nullable=False, server_default=sa.false()),
        sa.Column('created_at', sa.DateTime(timezone=True), nullable=False, server_default=sa.func.now()),
    )


def downgrade() -> None:
    op.drop_table('outbox_events')
    op.drop_table('recommendations')
    op.drop_table('assessment_answers')
    op.drop_table('assessments')
    op.drop_table('question_options')
    op.drop_table('questions')
    op.drop_table('users')
