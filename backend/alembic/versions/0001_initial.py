"""initial schema

Revision ID: 0001
Revises:
"""

import sqlalchemy as sa
from alembic import op

revision = "0001"
down_revision = None
branch_labels = None
depends_on = None


def _prospect_child_table(
    table_name: str,
    *columns: sa.Column,
) -> None:
    op.create_table(
        table_name,
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "prospect_id",
            sa.Integer(),
            sa.ForeignKey("prospects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        *columns,
    )
    op.create_index(f"ix_{table_name}_prospect_id", table_name, ["prospect_id"])


def upgrade() -> None:
    op.create_table(
        "prospects",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("dedup_key", sa.String(64), nullable=False),
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
        sa.Column("score_version", sa.String(40)),
        sa.Column("score_explanation", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_prospects_dedup_key", "prospects", ["dedup_key"], unique=True)
    op.create_index("ix_prospects_name", "prospects", ["name"])
    op.create_index("ix_prospects_niche", "prospects", ["niche"])
    op.create_index("ix_prospects_city", "prospects", ["city"])
    op.create_index("ix_prospects_state", "prospects", ["state"])
    op.create_index("ix_prospects_status", "prospects", ["status"])

    _prospect_child_table(
        "evidence",
        sa.Column("key", sa.String(120), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("source", sa.String(500), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("observed_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_evidence_key", "evidence", ["key"])

    _prospect_child_table(
        "score_components",
        sa.Column("signal", sa.String(120), nullable=False),
        sa.Column("value", sa.JSON(), nullable=False),
        sa.Column("weight", sa.Integer(), nullable=False),
        sa.Column("contribution", sa.Integer(), nullable=False),
        sa.Column("rationale", sa.Text(), nullable=False),
    )
    _prospect_child_table(
        "opportunities",
        sa.Column("kind", sa.String(120), nullable=False),
        sa.Column("title", sa.String(200), nullable=False),
        sa.Column("hypothesis", sa.Text(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
    )
    _prospect_child_table(
        "outreach_drafts",
        sa.Column("channel", sa.String(40), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    _prospect_child_table(
        "demos",
        sa.Column("template_key", sa.String(120), nullable=False),
        sa.Column("payload", sa.JSON(), nullable=False),
        sa.Column("is_fictional", sa.Boolean(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    _prospect_child_table(
        "crm_activities",
        sa.Column("activity_type", sa.String(80), nullable=False),
        sa.Column("from_status", sa.String(40)),
        sa.Column("to_status", sa.String(40)),
        sa.Column("note", sa.Text()),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )


def downgrade() -> None:
    for table_name in (
        "crm_activities",
        "demos",
        "outreach_drafts",
        "opportunities",
        "score_components",
        "evidence",
    ):
        op.drop_table(table_name)
    op.drop_table("prospects")
