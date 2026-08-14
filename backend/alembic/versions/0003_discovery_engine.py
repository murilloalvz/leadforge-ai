"""discovery engine

Revision ID: 0003
Revises: 0002
"""

import sqlalchemy as sa
from alembic import op

revision = "0003"
down_revision = "0002"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "discovery_runs",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column("niche", sa.String(160), nullable=False),
        sa.Column("city", sa.String(120), nullable=False),
        sa.Column("state", sa.String(2), nullable=False),
        sa.Column("provider", sa.String(80), nullable=False),
        sa.Column("requested_limit", sa.Integer(), nullable=False),
        sa.Column("analyze_sites", sa.Boolean(), nullable=False),
        sa.Column("site_audit_limit", sa.Integer(), nullable=False),
        sa.Column("status", sa.String(40), nullable=False),
        sa.Column("discovered_count", sa.Integer(), nullable=False),
        sa.Column("created_count", sa.Integer(), nullable=False),
        sa.Column("reused_count", sa.Integer(), nullable=False),
        sa.Column("audited_count", sa.Integer(), nullable=False),
        sa.Column("audit_failure_count", sa.Integer(), nullable=False),
        sa.Column("error_message", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("completed_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_discovery_runs_niche", "discovery_runs", ["niche"])
    op.create_index("ix_discovery_runs_city", "discovery_runs", ["city"])
    op.create_index("ix_discovery_runs_state", "discovery_runs", ["state"])
    op.create_index("ix_discovery_runs_provider", "discovery_runs", ["provider"])
    op.create_index("ix_discovery_runs_status", "discovery_runs", ["status"])
    op.create_index("ix_discovery_runs_created_at", "discovery_runs", ["created_at"])

    op.create_table(
        "discovery_candidates",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "run_id",
            sa.Integer(),
            sa.ForeignKey("discovery_runs.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "prospect_id",
            sa.Integer(),
            sa.ForeignKey("prospects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "site_audit_id",
            sa.Integer(),
            sa.ForeignKey("site_audits.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("source_external_id", sa.String(160), nullable=False),
        sa.Column("source_url", sa.String(2000), nullable=True),
        sa.Column("source_category", sa.String(300), nullable=True),
        sa.Column("source_payload", sa.JSON(), nullable=False),
        sa.Column("automation_score", sa.Integer(), nullable=False),
        sa.Column("automation_confidence", sa.Float(), nullable=False),
        sa.Column("ai_discoverability_score", sa.Integer(), nullable=True),
        sa.Column("ai_discoverability_confidence", sa.Float(), nullable=True),
        sa.Column("priority_bucket", sa.String(60), nullable=False),
        sa.Column("rank", sa.Integer(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index("ix_discovery_candidates_run_id", "discovery_candidates", ["run_id"])
    op.create_index(
        "ix_discovery_candidates_prospect_id",
        "discovery_candidates",
        ["prospect_id"],
    )
    op.create_index(
        "ix_discovery_candidates_site_audit_id",
        "discovery_candidates",
        ["site_audit_id"],
    )
    op.create_index(
        "ix_discovery_candidates_priority_bucket",
        "discovery_candidates",
        ["priority_bucket"],
    )
    op.create_index("ix_discovery_candidates_rank", "discovery_candidates", ["rank"])


def downgrade() -> None:
    op.drop_index("ix_discovery_candidates_rank", table_name="discovery_candidates")
    op.drop_index(
        "ix_discovery_candidates_priority_bucket",
        table_name="discovery_candidates",
    )
    op.drop_index(
        "ix_discovery_candidates_site_audit_id",
        table_name="discovery_candidates",
    )
    op.drop_index(
        "ix_discovery_candidates_prospect_id",
        table_name="discovery_candidates",
    )
    op.drop_index("ix_discovery_candidates_run_id", table_name="discovery_candidates")
    op.drop_table("discovery_candidates")

    op.drop_index("ix_discovery_runs_created_at", table_name="discovery_runs")
    op.drop_index("ix_discovery_runs_status", table_name="discovery_runs")
    op.drop_index("ix_discovery_runs_provider", table_name="discovery_runs")
    op.drop_index("ix_discovery_runs_state", table_name="discovery_runs")
    op.drop_index("ix_discovery_runs_city", table_name="discovery_runs")
    op.drop_index("ix_discovery_runs_niche", table_name="discovery_runs")
    op.drop_table("discovery_runs")
