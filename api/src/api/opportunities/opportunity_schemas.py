from typing import Any

from marshmallow import post_load

from src.api.feature_flags.feature_flag import FeatureFlag
from src.api.feature_flags.feature_flag_config import FeatureFlagConfig, get_feature_flag_config
from src.api.schemas.extension import Schema, fields
from src.constants.lookup_constants import OpportunityCategory, OpportunityStatus
from src.pagination.pagination_schema import PaginationSchema, generate_sorting_schema


class OpportunityV0Schema(Schema):
    opportunity_id = fields.Integer(
        dump_only=True,
        metadata={"description": "The internal ID of the opportunity", "example": 12345},
    )

    opportunity_number = fields.String(
        metadata={"description": "The funding opportunity number", "example": "ABC-123-XYZ-001"}
    )
    opportunity_title = fields.String(
        metadata={
            "description": "The title of the opportunity",
            "example": "Research into conservation techniques",
        }
    )
    agency = fields.String(
        metadata={"description": "The agency who created the opportunity", "example": "US-ABC"}
    )

    category = fields.Enum(
        OpportunityCategory,
        metadata={
            "description": "The opportunity category",
            "example": OpportunityCategory.DISCRETIONARY,
        },
    )
    category_explanation = fields.String(
        metadata={
            "description": "Explanation of the category when the category is 'O' (other)",
            "example": None,
        }
    )

    revision_number = fields.Integer(
        metadata={
            "description": "The current revision number of the opportunity, counting starts at 0",
            "example": 0,
        }
    )
    modified_comments = fields.String(
        metadata={
            "description": "Details regarding what modification was last made",
            "example": None,
        }
    )

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)


class OpportunitySearchV0Schema(Schema):
    opportunity_title = fields.String(
        metadata={
            "description": "The title of the opportunity to search for",
            "example": "research",
        }
    )
    category = fields.Enum(
        OpportunityCategory,
        metadata={
            "description": "The opportunity category to search for",
            "example": OpportunityCategory.DISCRETIONARY,
        },
    )

    sorting = fields.Nested(
        generate_sorting_schema(
            "OpportunitySortingSchema",
            order_by_fields=[
                "opportunity_id",
                "agency",
                "opportunity_number",
                "created_at",
                "updated_at",
            ],
        )(),
        required=True,
    )
    paging = fields.Nested(PaginationSchema(), required=True)


class OpportunitySearchHeaderV0Schema(Schema):
    # Header field: FF-Enable-Opportunity-Log-Msg
    enable_opportunity_log_msg = fields.Boolean(
        data_key=FeatureFlag.ENABLE_OPPORTUNITY_LOG_MSG.get_header_name(),
        metadata={"description": "Whether to log a message in the opportunity endpoint"},
    )

    @post_load
    def post_load(self, data: dict, **kwargs: Any) -> FeatureFlagConfig:
        """
        Merge the default feature flag values with any header overrides.

        Then return the FeatureFlagConfig object rather than a dictionary.
        """
        feature_flag_config = get_feature_flag_config()

        enable_opportunity_log_msg = data.get("enable_opportunity_log_msg", None)
        if enable_opportunity_log_msg is not None:
            feature_flag_config.enable_opportunity_log_msg = enable_opportunity_log_msg

        return feature_flag_config


#########################
# v0.1 models
#########################

class OpportunitySummaryV01Schema(Schema):

    opportunity_status = fields.Enum(OpportunityStatus)

    summary_description = fields.String()
    is_cost_sharing = fields.Boolean()

    close_date = fields.Date()
    close_date_description = fields.String()

    post_date = fields.Date()
    archive_date = fields.Date()
    # not including unarchive date at the moment

    expected_number_of_awards = fields.Integer()
    estimated_total_program_funding = fields.Integer()
    award_floor = fields.Integer()
    award_ceiling = fields.Integer()

class OpportunityAssistanceListingV01Schema(Schema):

    program_title = fields.String()
    assistance_listing_number = fields.String()

class OpportunityV01Schema(Schema):
    opportunity_id = fields.Integer(
        dump_only=True,
        metadata={"description": "The internal ID of the opportunity", "example": 12345},
    )

    opportunity_number = fields.String(
        metadata={"description": "The funding opportunity number", "example": "ABC-123-XYZ-001"}
    )
    opportunity_title = fields.String(
        metadata={
            "description": "The title of the opportunity",
            "example": "Research into conservation techniques",
        }
    )
    agency = fields.String(
        metadata={"description": "The agency who created the opportunity", "example": "US-ABC"}
    )

    category = fields.Enum(
        OpportunityCategory,
        metadata={
            "description": "The opportunity category",
            "example": OpportunityCategory.DISCRETIONARY,
        },
    )
    category_explanation = fields.String(
        metadata={
            "description": "Explanation of the category when the category is 'O' (other)",
            "example": None,
        }
    )

    revision_number = fields.Integer(
        metadata={
            "description": "The current revision number of the opportunity, counting starts at 0",
            "example": 0,
        }
    )
    modified_comments = fields.String(
        metadata={
            "description": "Details regarding what modification was last made",
            "example": None,
        }
    )

    created_at = fields.DateTime(dump_only=True)
    updated_at = fields.DateTime(dump_only=True)