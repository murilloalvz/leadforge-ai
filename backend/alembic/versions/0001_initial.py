"""initial schema

Revision ID: 0001
Revises:
"""
from alembic import op
import sqlalchemy as sa

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "prospects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("name", sa.String(200), nullable=False),
        sa.Column("niche", sa.String(120), nullable=False),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("state", sa.String(2), nullable=False),
        sa.Column("website", sa.String(500)),
        sa.Column("phone", sa.String(40)),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("is_fictional", sa.Boolean(), nullable=False),
        sa.Column("score", sa.Integer()),
        sa.Column("score_confidence", sa.Float()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_prospects_name", "prospects", ["name"])
    op.create_index("ix_prospects_niche", "prospects", ["niche"])
    op.create_index("ix_prospects_city", "prospects", ["city"])
    op.create_index("ix_prospects_state", "prospects", ["state"])
    op.create_index("ix_prospects_status", "prospects", ["status"])

    tables = (
        ("evidence", [sa.Column("key", sa.String(120), nullable=False), sa.Column("value", sa.JSON(), nullable=False), sa.Column("source", sa.String(500), nullable=False), sa.Column("confidence", sa.Float(), nullable=False), sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False)]),
        ("score_components", [sa.Column("signal", sa.String(120), nullable=False), sa.Column("value", sa.JSON(), nullable=False), sa.Column("weight", sa.Integer(), nullable=False), sa.Column("contribution", sa.Integer(), nullable=False), sa.Column("rationale", sa.Text(), nullable=False)]),
        ("opportunities", [sa.Column("kind", sa.String(120), nullable=False), sa.Column("title", sa.String(200), nullable=False), sa.Column("hypothesis", sa.Text(), nullable=False), sa.Column("confidence", sa.Float(), nullable=False), sa.Column("status", sa.String(40), nullable=False)]),
        ("outreach_drafts", [sa.Column("channel", sa.String(40), nullable=False), sa.Column("body", sa.Text(), nullable=False), sa.Column("status", sa.String(40), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)]),
        ("demos", [sa.Column("template_key", sa.String(120), nullable=False), sa.Column("payload", sa.JSON(), nullable=False), sa.Column("is_fictional", sa.Boolean(), nullable=False), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)]),
        ("crm_activities", [sa.Column("activity_type", sa.String(80), nullable=False), sa.Column("from_status", sa.String(40)), sa.Column("to_status", sa.String(40)), sa.Column("note", sa.Text()), sa.Column("created_at", sa.DateTime(timezone=True), nullable=False)]),
    )
    for table_name, columns in tables:
        op.create_table(
            table_name,
            sa.Column("id", sa.Integer(), primary_key=True),
            sa.Column("prospect_id", sa.Integer(), sa.ForeignKey("prospects.id", ondelete="CASCADE"), nullable=False),
            *columns,
        )
        op.create_index(f"ix_{table_name}_prospect_id", table_name, ["prospect_id"])
    op.create_index("ix_evidence_key", "evidence", ["key"])


def downgrade() -> None:
    for table_name in ("crm_activities", "demos", "outreach_drafts", "opportunities", "score_components", "evidence"):
        op.drop_table(table_name)
    op.drop_table("prospects")
