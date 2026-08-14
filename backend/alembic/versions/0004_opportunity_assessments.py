"""generic opportunity assessments

Revision ID: 0004
Revises: 0003
"""

import sqlalchemy as sa
from alembic import op

revision = "0004"
down_revision = "0003"
branch_labels = None
depends_on = None


def upgrade() -> None:
    op.create_table(
        "opportunity_assessments",
        sa.Column("id", sa.Integer(), primary_key=True),
        sa.Column(
            "prospect_id",
            sa.Integer(),
            sa.ForeignKey("prospects.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column(
            "discovery_run_id",
            sa.Integer(),
            sa.ForeignKey("discovery_runs.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column(
            "site_audit_id",
            sa.Integer(),
            sa.ForeignKey("site_audits.id", ondelete="SET NULL"),
            nullable=True,
        ),
        sa.Column("service_category", sa.String(80), nullable=False),
        sa.Column("score", sa.Integer(), nullable=False),
        sa.Column("confidence", sa.Float(), nullable=False),
        sa.Column("version", sa.String(80), nullable=False),
        sa.Column("summary", sa.Text(), nullable=False),
        sa.Column("recommended_service", sa.String(240), nullable=True),
        sa.Column("findings", sa.JSON(), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), nullable=False),
    )
    op.create_index(
        "ix_opportunity_assessments_prospect_id",
        "opportunity_assessments",
        ["prospect_id"],
    )
    op.create_index(
        "ix_opportunity_assessments_discovery_run_id",
        "opportunity_assessments",
        ["discovery_run_id"],
    )
    op.create_index(
        "ix_opportunity_assessments_site_audit_id",
        "opportunity_assessments",
        ["site_audit_id"],
    )
    op.create_index(
        "ix_opportunity_assessments_service_category",
        "opportunity_assessments",
        ["service_category"],
    )
    op.create_index(
        "ix_opportunity_assessments_score",
        "opportunity_assessments",
        ["score"],
    )
    op.create_index(
        "ix_opportunity_assessments_version",
        "opportunity_assessments",
        ["version"],
    )
    op.create_index(
        "ix_opportunity_assessments_created_at",
        "opportunity_assessments",
        ["created_at"],
    )

    with op.batch_alter_table("discovery_candidates") as batch_op:
        batch_op.add_column(
            sa.Column("opportunity_assessment_id", sa.Integer(), nullable=True)
        )
        batch_op.create_foreign_key(
            "fk_discovery_candidates_opportunity_assessment_id",
            "opportunity_assessments",
            ["opportunity_assessment_id"],
            ["id"],
            ondelete="SET NULL",
        )
        batch_op.create_index(
            "ix_discovery_candidates_opportunity_assessment_id",
            ["opportunity_assessment_id"],
        )


def downgrade() -> None:
    with op.batch_alter_table("discovery_candidates") as batch_op:
        batch_op.drop_index("ix_discovery_candidates_opportunity_assessment_id")
        batch_op.drop_constraint(
            "fk_discovery_candidates_opportunity_assessment_id",
            type_="foreignkey",
        )
        batch_op.drop_column("opportunity_assessment_id")

    op.drop_index(
        "ix_opportunity_assessments_created_at",
        table_name="opportunity_assessments",
    )
    op.drop_index(
        "ix_opportunity_assessments_version",
        table_name="opportunity_assessments",
    )
    op.drop_index(
        "ix_opportunity_assessments_score",
        table_name="opportunity_assessments",
    )
    op.drop_index(
        "ix_opportunity_assessments_service_category",
        table_name="opportunity_assessments",
    )
    op.drop_index(
        "ix_opportunity_assessments_site_audit_id",
        table_name="opportunity_assessments",
    )
    op.drop_index(
        "ix_opportunity_assessments_discovery_run_id",
        table_name="opportunity_assessments",
    )
    op.drop_index(
        "ix_opportunity_assessments_prospect_id",
        table_name="opportunity_assessments",
    )
    op.drop_table("opportunity_assessments")
