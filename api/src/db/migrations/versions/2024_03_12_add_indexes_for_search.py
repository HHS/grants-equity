"""Add indexes for search

Revision ID: f8364285630d
Revises: 578c80acb29c
Create Date: 2024-03-12 13:22:57.718265

"""

from alembic import op

# revision identifiers, used by Alembic.
revision = "f8364285630d"
down_revision = "578c80acb29c"
branch_labels = None
depends_on = None


def upgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.create_index(
        op.f("current_opportunity_summary_opportunity_id_idx"),
        "current_opportunity_summary",
        ["opportunity_id"],
        unique=False,
        schema="api",
    )
    op.create_index(
        op.f("current_opportunity_summary_opportunity_status_id_idx"),
        "current_opportunity_summary",
        ["opportunity_status_id"],
        unique=False,
        schema="api",
    )
    op.create_index(
        op.f("current_opportunity_summary_opportunity_summary_id_idx"),
        "current_opportunity_summary",
        ["opportunity_summary_id"],
        unique=False,
        schema="api",
    )
    op.create_index(
        op.f("link_opportunity_summary_applicant_type_applicant_type_id_idx"),
        "link_opportunity_summary_applicant_type",
        ["applicant_type_id"],
        unique=False,
        schema="api",
    )
    op.create_index(
        op.f("link_opportunity_summary_applicant_type_opportunity_summary_id_idx"),
        "link_opportunity_summary_applicant_type",
        ["opportunity_summary_id"],
        unique=False,
        schema="api",
    )
    op.create_index(
        op.f("link_opportunity_summary_funding_category_funding_category_id_idx"),
        "link_opportunity_summary_funding_category",
        ["funding_category_id"],
        unique=False,
        schema="api",
    )
    op.create_index(
        op.f("link_opportunity_summary_funding_category_opportunity_summary_id_idx"),
        "link_opportunity_summary_funding_category",
        ["opportunity_summary_id"],
        unique=False,
        schema="api",
    )
    op.create_index(
        op.f("link_opportunity_summary_funding_instrument_funding_instrument_id_idx"),
        "link_opportunity_summary_funding_instrument",
        ["funding_instrument_id"],
        unique=False,
        schema="api",
    )
    op.create_index(
        op.f("link_opportunity_summary_funding_instrument_opportunity_summary_id_idx"),
        "link_opportunity_summary_funding_instrument",
        ["opportunity_summary_id"],
        unique=False,
        schema="api",
    )
    op.create_index(
        op.f("opportunity_agency_idx"), "opportunity", ["agency"], unique=False, schema="api"
    )
    op.create_index(
        op.f("opportunity_summary_opportunity_id_idx"),
        "opportunity_summary",
        ["opportunity_id"],
        unique=False,
        schema="api",
    )
    # ### end Alembic commands ###


def downgrade():
    # ### commands auto generated by Alembic - please adjust! ###
    op.drop_index(
        op.f("opportunity_summary_opportunity_id_idx"),
        table_name="opportunity_summary",
        schema="api",
    )
    op.drop_index(op.f("opportunity_agency_idx"), table_name="opportunity", schema="api")
    op.drop_index(
        op.f("link_opportunity_summary_funding_instrument_opportunity_summary_id_idx"),
        table_name="link_opportunity_summary_funding_instrument",
        schema="api",
    )
    op.drop_index(
        op.f("link_opportunity_summary_funding_instrument_funding_instrument_id_idx"),
        table_name="link_opportunity_summary_funding_instrument",
        schema="api",
    )
    op.drop_index(
        op.f("link_opportunity_summary_funding_category_opportunity_summary_id_idx"),
        table_name="link_opportunity_summary_funding_category",
        schema="api",
    )
    op.drop_index(
        op.f("link_opportunity_summary_funding_category_funding_category_id_idx"),
        table_name="link_opportunity_summary_funding_category",
        schema="api",
    )
    op.drop_index(
        op.f("link_opportunity_summary_applicant_type_opportunity_summary_id_idx"),
        table_name="link_opportunity_summary_applicant_type",
        schema="api",
    )
    op.drop_index(
        op.f("link_opportunity_summary_applicant_type_applicant_type_id_idx"),
        table_name="link_opportunity_summary_applicant_type",
        schema="api",
    )
    op.drop_index(
        op.f("current_opportunity_summary_opportunity_summary_id_idx"),
        table_name="current_opportunity_summary",
        schema="api",
    )
    op.drop_index(
        op.f("current_opportunity_summary_opportunity_status_id_idx"),
        table_name="current_opportunity_summary",
        schema="api",
    )
    op.drop_index(
        op.f("current_opportunity_summary_opportunity_id_idx"),
        table_name="current_opportunity_summary",
        schema="api",
    )
    # ### end Alembic commands ###
