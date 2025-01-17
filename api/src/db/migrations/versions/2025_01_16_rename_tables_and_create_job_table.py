"""Rename tables and create job table

Revision ID: dc04ce955a9a
Revises: 99bb8e01ad38
Create Date: 2025-01-16 18:34:48.013913

"""

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql
from sqlalchemy.sql import text

# revision identifiers, used by Alembic.
revision = "dc04ce955a9a"
down_revision = "99bb8e01ad38"
branch_labels = None
depends_on = None


create_trigger_function = """
CREATE OR REPLACE FUNCTION update_opportunity_search_queue()
RETURNS TRIGGER AS $$
DECLARE
    opp_id bigint;
BEGIN
    -- Determine the opportunity_id based on the table
    CASE TG_TABLE_NAME
        WHEN 'link_opportunity_summary_funding_instrument' THEN
            opp_id := (SELECT opportunity_id FROM api.opportunity_summary WHERE opportunity_summary_id = NEW.opportunity_summary_id);
        WHEN 'link_opportunity_summary_funding_category' THEN
            opp_id := (SELECT opportunity_id FROM api.opportunity_summary WHERE opportunity_summary_id = NEW.opportunity_summary_id);
        WHEN 'link_opportunity_summary_applicant_type' THEN
            opp_id := (SELECT opportunity_id FROM api.opportunity_summary WHERE opportunity_summary_id = NEW.opportunity_summary_id);
        WHEN 'opportunity_summary' THEN
            opp_id := NEW.opportunity_id;
        WHEN 'current_opportunity_summary' THEN
            opp_id := NEW.opportunity_id;
        ELSE
            opp_id := NEW.opportunity_id;
    END CASE;

    INSERT INTO api.opportunity_change_audit (opportunity_id, has_update)
    VALUES (opp_id, TRUE)
    ON CONFLICT (opportunity_id)
    DO UPDATE SET has_update = TRUE, updated_at = CURRENT_TIMESTAMP;

    RETURN NEW;
END;
$$ LANGUAGE plpgsql;
"""


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "job",
        sa.Column("job_id", sa.UUID(), nullable=False),
        sa.Column("job_type", sa.Text(), nullable=False),
        sa.Column(
            "job_status",
            sa.Text(),
            nullable=False,
        ),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.PrimaryKeyConstraint("job_id", name=op.f("job_pkey")),
        schema="api",
    )
    op.create_table(
        "opportunity_change_audit",
        sa.Column("opportunity_id", sa.BigInteger(), nullable=False),
        sa.Column("last_loaded_at", sa.TIMESTAMP(timezone=True), nullable=True),
        sa.Column("has_update", sa.Boolean(), nullable=False),
        sa.Column(
            "created_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            sa.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["opportunity_id"],
            ["api.opportunity.opportunity_id"],
            name=op.f("opportunity_change_audit_opportunity_id_opportunity_fkey"),
        ),
        sa.PrimaryKeyConstraint("opportunity_id", name=op.f("opportunity_change_audit_pkey")),
        schema="api",
    )
    op.create_index(
        op.f("opportunity_change_audit_opportunity_id_idx"),
        "opportunity_change_audit",
        ["opportunity_id"],
        unique=False,
        schema="api",
    )

    op.execute(create_trigger_function)

    # Insert all existing opportunities into the audit table
    op.execute(
        text(
            """
            INSERT INTO api.opportunity_change_audit (opportunity_id, last_loaded_at, created_at, updated_at)
            SELECT 
                opportunity_id,
                updated_at as last_loaded_at,
                CURRENT_TIMESTAMP as created_at,
                CURRENT_TIMESTAMP as updated_at
            FROM api.opportunity
            ON CONFLICT (opportunity_id) DO NOTHING
            """
        )
    )

    op.drop_index(
        "opportunity_search_index_queue_opportunity_id_idx",
        table_name="opportunity_search_index_queue",
        schema="api",
    )
    op.drop_table("opportunity_search_index_queue", schema="api")
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_table(
        "opportunity_search_index_queue",
        sa.Column("opportunity_id", sa.BIGINT(), autoincrement=False, nullable=False),
        sa.Column(
            "created_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.Column(
            "updated_at",
            postgresql.TIMESTAMP(timezone=True),
            server_default=sa.text("now()"),
            autoincrement=False,
            nullable=False,
        ),
        sa.ForeignKeyConstraint(
            ["opportunity_id"],
            ["api.opportunity.opportunity_id"],
            name="opportunity_search_index_queue_opportunity_id_opportunity_fkey",
        ),
        sa.PrimaryKeyConstraint("opportunity_id", name="opportunity_search_index_queue_pkey"),
        schema="api",
    )
    op.create_index(
        "opportunity_search_index_queue_opportunity_id_idx",
        "opportunity_search_index_queue",
        ["opportunity_id"],
        unique=False,
        schema="api",
    )
    op.drop_index(
        op.f("opportunity_change_audit_opportunity_id_idx"),
        table_name="opportunity_change_audit",
        schema="api",
    )
    op.drop_table("opportunity_change_audit", schema="api")
    op.drop_table("job", schema="api")
    # ### end Alembic commands ###
