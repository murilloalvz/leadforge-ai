"""site audits

Revision ID: 0002
Revises: 0001
"""

import sqlalchemy as sa
from alembic import op

revision = "0002"
down_revision = "0001"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "site_audits",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "prospect_id",
            sa.Integer(),
            sa.ForeignKey("prospects.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("requested_url", sa.String(2000), nullable=False),
        sa.Column("final_url", sa.String(2000), nullable=False),
        sa.Column("http_status", sa.Integer(), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("score_version", sa.String(80), nullable=False),
        sa.Column("signals", sa.JSON(), nullable=False),
        sa.Column("evidence", sa.JSON(), nullable=False),
        sa.Column("blockers", sa.JSON(), nullable=False),
        sa.Column("recommendations", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_site_audits_prospect_id", "site_audits", ["prospect_id"])
    op.create_index("ix_site_audits_score", "site_audits", ["score"])
    op.create_index("ix_site_audits_score_version", "site_audits", ["score_version"])
    op.create_index("ix_site_audits_created_at", "site_audits", ["created_at"])


def downgrade() -> None:
    op.drop_index("ix_site_audits_created_at", table_name="site_audits")
    op.drop_index("ix_site_audits_score_version", table_name="site_audits")
    op.drop_index("ix_site_audits_score", table_name="site_audits")
    op.drop_index("ix_site_audits_prospect_id", table_name="site_audits")
    op.drop_table("site_audits")
