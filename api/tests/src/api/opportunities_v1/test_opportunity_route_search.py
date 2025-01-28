import csv
from datetime import date

import pytest

from src.api.opportunities_v1.opportunity_schemas import OpportunityV1Schema
from src.constants.lookup_constants import (
    ApplicantType,
    FundingCategory,
    FundingInstrument,
    OpportunityStatus,
)
from src.db.models.opportunity_models import Opportunity
from src.pagination.pagination_models import SortDirection
from src.util.dict_util import flatten_dict
from tests.conftest import BaseTestClass
from tests.src.api.opportunities_v1.conftest import get_search_request
from tests.src.db.models.factories import (
    CurrentOpportunitySummaryFactory,
    OpportunityAssistanceListingFactory,
    OpportunityFactory,
    OpportunitySummaryFactory,
)


def validate_search_response(
    search_response,
    expected_results: list[Opportunity],
    expected_status_code: int = 200,
    is_csv_response: bool = False,
):
    assert search_response.status_code == expected_status_code

    expected_ids = [exp.opportunity_id for exp in expected_results]

    if is_csv_response:
        reader = csv.DictReader(search_response.text.split("\n"))
        opportunities = [record for record in reader]
    else:
        response_json = search_response.get_json()
        opportunities = response_json["data"]

    response_ids = [int(opp["opportunity_id"]) for opp in opportunities]

    for opp in opportunities:
        if "summary" in opp:
            assert "agency_phone_number" not in opp["summary"]

    assert (
        response_ids == expected_ids
    ), f"Actual opportunities:\n {'\n'.join([opp['opportunity_title'] for opp in opportunities])}"


def call_search_and_validate(client, api_auth_token, search_request, expected_results):
    resp = client.post(
        "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
    )
    validate_search_response(resp, expected_results)

    search_request["format"] = "csv"
    resp = client.post(
        "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
    )
    validate_search_response(resp, expected_results, is_csv_response=True)


def build_opp(
    opportunity_title: str,
    opportunity_number: str,
    agency: str,
    summary_description: str,
    opportunity_status: OpportunityStatus,
    assistance_listings: list,
    applicant_types: list,
    funding_instruments: list,
    funding_categories: list,
    post_date: date,
    close_date: date | None,
    is_cost_sharing: bool,
    expected_number_of_awards: int | None,
    award_floor: int | None,
    award_ceiling: int | None,
    estimated_total_program_funding: int | None,
    agency_phone_number: str | None = "123-456-7890",
) -> Opportunity:
    opportunity = OpportunityFactory.build(
        opportunity_title=opportunity_title,
        opportunity_number=opportunity_number,
        agency_code=agency,
        opportunity_assistance_listings=[],
        current_opportunity_summary=None,
    )

    for assistance_listing in assistance_listings:
        opportunity.opportunity_assistance_listings.append(
            OpportunityAssistanceListingFactory.build(
                opportunity=opportunity,
                assistance_listing_number=assistance_listing[0],
                program_title=assistance_listing[1],
            )
        )

    opportunity_summary = OpportunitySummaryFactory.build(
        opportunity=opportunity,
        summary_description=summary_description,
        applicant_types=applicant_types,
        funding_instruments=funding_instruments,
        funding_categories=funding_categories,
        post_date=post_date,
        close_date=close_date,
        is_cost_sharing=is_cost_sharing,
        expected_number_of_awards=expected_number_of_awards,
        award_floor=award_floor,
        award_ceiling=award_ceiling,
        estimated_total_program_funding=estimated_total_program_funding,
        agency_phone_number=agency_phone_number,
    )

    opportunity.current_opportunity_summary = CurrentOpportunitySummaryFactory.build(
        opportunity_status=opportunity_status,
        opportunity_summary=opportunity_summary,
        opportunity=opportunity,
    )

    return opportunity


##########################################
# Opportunity scenarios for tests
#
# These try to mimic real opportunities
##########################################

EDUCATION_AL = ("43.008", "Office of Stem Engagement (OSTEM)")
SPACE_AL = ("43.012", "Space Technology")
AERONAUTICS_AL = ("43.002", "Aeronautics")
LOC_AL = ("42.011", "Library of Congress Grants")
AMERICAN_AL = ("19.441", "ECA - American Spaces")
ECONOMIC_AL = ("11.307", "Economic Adjustment Assistance")
MANUFACTURING_AL = ("11.611", "Manufacturing Extension Partnership")

NASA_SPACE_FELLOWSHIP = build_opp(
    opportunity_title="National Space Grant College and Fellowship Program FY 2020 - 2024",
    opportunity_number="NNH123ZYX",
    agency="NASA",
    summary_description="This Cooperative Agreement Notice is a multi-year award that aims to contribute to NASA's mission",
    opportunity_status=OpportunityStatus.POSTED,
    assistance_listings=[EDUCATION_AL],
    applicant_types=[ApplicantType.OTHER],
    funding_instruments=[FundingInstrument.COOPERATIVE_AGREEMENT],
    funding_categories=[FundingCategory.EDUCATION],
    post_date=date(2020, 3, 1),
    close_date=date(2027, 6, 1),
    is_cost_sharing=True,
    expected_number_of_awards=3,
    award_floor=50_000,
    award_ceiling=5_000_000,
    estimated_total_program_funding=15_000_000,
    agency_phone_number="123-456-7890",
)

NASA_INNOVATIONS = build_opp(
    opportunity_title="Early Stage Innovations",
    opportunity_number="NNH24-TR0N",
    agency="NASA",
    summary_description="The program within STMD seeks proposals from accredited U.S. universities to develop unique, disruptive, or transformational space technologies.",
    opportunity_status=OpportunityStatus.FORECASTED,
    assistance_listings=[SPACE_AL],
    applicant_types=[ApplicantType.OTHER],
    funding_instruments=[FundingInstrument.GRANT],
    funding_categories=[FundingCategory.SCIENCE_TECHNOLOGY_AND_OTHER_RESEARCH_AND_DEVELOPMENT],
    post_date=date(2019, 3, 1),
    close_date=None,
    is_cost_sharing=False,
    expected_number_of_awards=1,
    award_floor=5000,
    award_ceiling=5000,
    estimated_total_program_funding=5000,
)

NASA_SUPERSONIC = build_opp(
    opportunity_title="Commercial Supersonic Technology (CST) Project",
    opportunity_number="NNH24-CST",
    agency="NASA",
    summary_description="Commercial Supersonic Technology seeks proposals for a fuel injector design concept and fabrication for testing at NASA Glenn Research Center",
    opportunity_status=OpportunityStatus.CLOSED,
    assistance_listings=[AERONAUTICS_AL],
    applicant_types=[ApplicantType.UNRESTRICTED],
    funding_instruments=[FundingInstrument.GRANT],
    funding_categories=[FundingCategory.SCIENCE_TECHNOLOGY_AND_OTHER_RESEARCH_AND_DEVELOPMENT],
    post_date=date(2021, 3, 1),
    close_date=date(2030, 6, 1),
    is_cost_sharing=True,
    expected_number_of_awards=9,
    award_floor=10_000,
    award_ceiling=50_000,
    estimated_total_program_funding=None,
)

NASA_K12_DIVERSITY = build_opp(
    opportunity_title="Space Grant K-12 Inclusiveness and Diversity in STEM",
    opportunity_number="NNH22ZHA",
    agency="NASA",
    summary_description="Expands the reach of individual Consortia to collaborate regionally on efforts that directly support middle and high school student participation in hands-on, NASA-aligned STEM activities",
    opportunity_status=OpportunityStatus.ARCHIVED,
    assistance_listings=[EDUCATION_AL],
    applicant_types=[ApplicantType.OTHER],
    funding_instruments=[FundingInstrument.COOPERATIVE_AGREEMENT],
    funding_categories=[FundingCategory.EDUCATION],
    post_date=date(2025, 3, 1),
    close_date=date(2018, 6, 1),
    is_cost_sharing=False,
    expected_number_of_awards=None,
    award_floor=None,
    award_ceiling=None,
    estimated_total_program_funding=None,
)

LOC_TEACHING = build_opp(
    opportunity_title="Teaching with Primary Sources - New Awards for FY25-FY27",
    opportunity_number="012ADV345",
    agency="LOC",
    summary_description="Builds student literacy, critical thinking skills, content knowledge and ability to conduct original research.",
    opportunity_status=OpportunityStatus.POSTED,
    assistance_listings=[EDUCATION_AL],
    applicant_types=[
        ApplicantType.STATE_GOVERNMENTS,
        ApplicantType.COUNTY_GOVERNMENTS,
        ApplicantType.INDEPENDENT_SCHOOL_DISTRICTS,
        ApplicantType.CITY_OR_TOWNSHIP_GOVERNMENTS,
        ApplicantType.SPECIAL_DISTRICT_GOVERNMENTS,
    ],
    funding_instruments=[FundingInstrument.COOPERATIVE_AGREEMENT],
    funding_categories=[FundingCategory.EDUCATION],
    post_date=date(2031, 3, 1),
    close_date=date(2010, 6, 1),
    is_cost_sharing=True,
    expected_number_of_awards=100,
    award_floor=500,
    award_ceiling=1_000,
    estimated_total_program_funding=10_000,
)

LOC_HIGHER_EDUCATION = build_opp(
    opportunity_title="Of the People: Widening the Path: CCDI – Higher Education",
    opportunity_number="012ADV346",
    agency="LOC",
    summary_description="The Library of Congress will expand the connections between the Library and diverse communities and strengthen the use of Library of Congress digital collections and digital tools",
    opportunity_status=OpportunityStatus.FORECASTED,
    assistance_listings=[LOC_AL],
    applicant_types=[
        ApplicantType.PRIVATE_INSTITUTIONS_OF_HIGHER_EDUCATION,
        ApplicantType.PUBLIC_AND_STATE_INSTITUTIONS_OF_HIGHER_EDUCATION,
    ],
    funding_instruments=[FundingInstrument.GRANT],
    funding_categories=[FundingCategory.OTHER],
    post_date=date(2026, 3, 1),
    close_date=None,
    is_cost_sharing=False,
    expected_number_of_awards=1,
    award_floor=None,
    award_ceiling=None,
    estimated_total_program_funding=15_000_000,
)

DOS_DIGITAL_LITERACY = build_opp(
    opportunity_title="American Spaces Digital Literacy and Training Program",
    opportunity_number="SFOP0001234",
    agency="DOS-ECA",
    summary_description="An open competition to administer a new award in the field of digital and media literacy and countering disinformation",
    opportunity_status=OpportunityStatus.CLOSED,
    assistance_listings=[AMERICAN_AL],
    applicant_types=[
        ApplicantType.OTHER,
        ApplicantType.NONPROFITS_NON_HIGHER_EDUCATION_WITH_501C3,
        ApplicantType.PRIVATE_INSTITUTIONS_OF_HIGHER_EDUCATION,
        ApplicantType.PUBLIC_AND_STATE_INSTITUTIONS_OF_HIGHER_EDUCATION,
    ],
    funding_instruments=[FundingInstrument.COOPERATIVE_AGREEMENT],
    funding_categories=[FundingCategory.OTHER],
    post_date=date(2028, 3, 1),
    close_date=date(2023, 6, 1),
    is_cost_sharing=True,
    expected_number_of_awards=2,
    award_floor=5,
    award_ceiling=10,
    estimated_total_program_funding=15,
)

DOC_SPACE_COAST = build_opp(
    opportunity_title="Space Coast RIC",
    opportunity_number="SFOP0009876",
    agency="DOC-EDA",
    summary_description="diversification of Florida's Space Coast region",
    opportunity_status=OpportunityStatus.ARCHIVED,
    assistance_listings=[ECONOMIC_AL],
    applicant_types=[
        ApplicantType.CITY_OR_TOWNSHIP_GOVERNMENTS,
        ApplicantType.COUNTY_GOVERNMENTS,
        ApplicantType.STATE_GOVERNMENTS,
    ],
    funding_instruments=[FundingInstrument.COOPERATIVE_AGREEMENT, FundingInstrument.GRANT],
    funding_categories=[FundingCategory.OTHER, FundingCategory.REGIONAL_DEVELOPMENT],
    post_date=date(2017, 3, 1),
    close_date=date(2019, 6, 1),
    is_cost_sharing=False,
    expected_number_of_awards=1000,
    award_floor=1,
    award_ceiling=2,
    estimated_total_program_funding=2000,
)

DOC_MANUFACTURING = build_opp(
    opportunity_title="Advanced Manufacturing Jobs and Innovation Accelerator Challenge",
    opportunity_number="JIAC1234AM",
    agency="DOC-EDA",
    summary_description="foster job creation, increase public and private investments, and enhance economic prosperity",
    opportunity_status=OpportunityStatus.POSTED,
    assistance_listings=[ECONOMIC_AL, MANUFACTURING_AL],
    applicant_types=[ApplicantType.OTHER],
    funding_instruments=[FundingInstrument.COOPERATIVE_AGREEMENT, FundingInstrument.GRANT],
    funding_categories=[
        FundingCategory.EMPLOYMENT_LABOR_AND_TRAINING,
        FundingCategory.ENERGY,
        FundingCategory.SCIENCE_TECHNOLOGY_AND_OTHER_RESEARCH_AND_DEVELOPMENT,
    ],
    post_date=date(2013, 3, 1),
    close_date=date(2035, 6, 1),
    is_cost_sharing=True,
    expected_number_of_awards=25,
    award_floor=50_000_000,
    award_ceiling=5_000_000_000,
    estimated_total_program_funding=15_000_000_000,
)

OPPORTUNITIES = [
    NASA_SPACE_FELLOWSHIP,
    NASA_INNOVATIONS,
    NASA_SUPERSONIC,
    NASA_K12_DIVERSITY,
    LOC_TEACHING,
    LOC_HIGHER_EDUCATION,
    DOS_DIGITAL_LITERACY,
    DOC_SPACE_COAST,
    DOC_MANUFACTURING,
]


def search_scenario_id_fnc(val):
    if isinstance(val, dict):
        return str(flatten_dict(val, separator="|"))


class TestOpportunityRouteSearch(BaseTestClass):
    @pytest.fixture(scope="class", autouse=True)
    def setup_search_data(self, opportunity_index, opportunity_index_alias, search_client):
        # Load into the search index
        schema = OpportunityV1Schema()
        json_records = [schema.dump(opportunity) for opportunity in OPPORTUNITIES]
        search_client.bulk_upsert(opportunity_index, json_records, "opportunity_id")

        # Swap the search index alias
        search_client.swap_alias_index(opportunity_index, opportunity_index_alias)

    @pytest.mark.parametrize(
        "search_request,expected_results",
        [
            # Opportunity ID
            (
                get_search_request(
                    page_size=25,
                    page_offset=1,
                    order_by="opportunity_id",
                    sort_direction=SortDirection.ASCENDING,
                ),
                OPPORTUNITIES,
            ),
            (
                get_search_request(
                    page_size=3,
                    page_offset=2,
                    order_by="opportunity_id",
                    sort_direction=SortDirection.ASCENDING,
                ),
                OPPORTUNITIES[3:6],
            ),
            (
                get_search_request(
                    page_size=25,
                    page_offset=1,
                    order_by="opportunity_id",
                    sort_direction=SortDirection.DESCENDING,
                ),
                OPPORTUNITIES[::-1],
            ),
            # Opportunity Number
            (
                get_search_request(
                    page_size=3,
                    page_offset=1,
                    order_by="opportunity_number",
                    sort_direction=SortDirection.ASCENDING,
                ),
                [LOC_TEACHING, LOC_HIGHER_EDUCATION, DOC_MANUFACTURING],
            ),
            (
                get_search_request(
                    page_size=2,
                    page_offset=3,
                    order_by="opportunity_number",
                    sort_direction=SortDirection.DESCENDING,
                ),
                [NASA_K12_DIVERSITY, NASA_SPACE_FELLOWSHIP],
            ),
            # Opportunity Title
            (
                get_search_request(
                    page_size=4,
                    page_offset=2,
                    order_by="opportunity_title",
                    sort_direction=SortDirection.ASCENDING,
                ),
                [NASA_SPACE_FELLOWSHIP, LOC_HIGHER_EDUCATION, DOC_SPACE_COAST, NASA_K12_DIVERSITY],
            ),
            (
                get_search_request(
                    page_size=5,
                    page_offset=1,
                    order_by="opportunity_title",
                    sort_direction=SortDirection.DESCENDING,
                ),
                [
                    LOC_TEACHING,
                    NASA_K12_DIVERSITY,
                    DOC_SPACE_COAST,
                    LOC_HIGHER_EDUCATION,
                    NASA_SPACE_FELLOWSHIP,
                ],
            ),
            # Post Date
            (
                get_search_request(
                    page_size=2,
                    page_offset=1,
                    order_by="post_date",
                    sort_direction=SortDirection.ASCENDING,
                ),
                [DOC_MANUFACTURING, DOC_SPACE_COAST],
            ),
            (
                get_search_request(
                    page_size=3,
                    page_offset=1,
                    order_by="post_date",
                    sort_direction=SortDirection.DESCENDING,
                ),
                [LOC_TEACHING, DOS_DIGITAL_LITERACY, LOC_HIGHER_EDUCATION],
            ),
            (
                get_search_request(
                    page_size=3,
                    page_offset=12,
                    order_by="post_date",
                    sort_direction=SortDirection.DESCENDING,
                ),
                [],
            ),
            # Relevancy has a secondary sort of post date so should be identical.
            (
                get_search_request(
                    page_size=2,
                    page_offset=1,
                    order_by="relevancy",
                    sort_direction=SortDirection.ASCENDING,
                ),
                [DOC_MANUFACTURING, DOC_SPACE_COAST],
            ),
            (
                get_search_request(
                    page_size=3,
                    page_offset=1,
                    order_by="relevancy",
                    sort_direction=SortDirection.DESCENDING,
                ),
                [LOC_TEACHING, DOS_DIGITAL_LITERACY, LOC_HIGHER_EDUCATION],
            ),
            (
                get_search_request(
                    page_size=3,
                    page_offset=12,
                    order_by="relevancy",
                    sort_direction=SortDirection.DESCENDING,
                ),
                [],
            ),
            # Close Date (note several have null values which always go to the end)
            (
                get_search_request(
                    page_size=4,
                    page_offset=1,
                    order_by="close_date",
                    sort_direction=SortDirection.ASCENDING,
                ),
                [LOC_TEACHING, NASA_K12_DIVERSITY, DOC_SPACE_COAST, DOS_DIGITAL_LITERACY],
            ),
            (
                get_search_request(
                    page_size=3,
                    page_offset=1,
                    order_by="close_date",
                    sort_direction=SortDirection.DESCENDING,
                ),
                [DOC_MANUFACTURING, NASA_SUPERSONIC, NASA_SPACE_FELLOWSHIP],
            ),
            # close date - but check the end of the list to find the null values
            (
                get_search_request(
                    page_size=5,
                    page_offset=2,
                    order_by="close_date",
                    sort_direction=SortDirection.ASCENDING,
                ),
                [NASA_SUPERSONIC, DOC_MANUFACTURING, NASA_INNOVATIONS, LOC_HIGHER_EDUCATION],
            ),
            # Agency
            (
                get_search_request(
                    page_size=5,
                    page_offset=1,
                    order_by="agency_code",
                    sort_direction=SortDirection.ASCENDING,
                ),
                [
                    DOC_SPACE_COAST,
                    DOC_MANUFACTURING,
                    DOS_DIGITAL_LITERACY,
                    LOC_TEACHING,
                    LOC_HIGHER_EDUCATION,
                ],
            ),
            (
                get_search_request(
                    page_size=3,
                    page_offset=1,
                    order_by="agency_code",
                    sort_direction=SortDirection.DESCENDING,
                ),
                [NASA_SPACE_FELLOWSHIP, NASA_INNOVATIONS, NASA_SUPERSONIC],
            ),
        ],
        ids=search_scenario_id_fnc,
    )
    def test_sorting_and_pagination_200(
        self, client, api_auth_token, search_request, expected_results
    ):
        call_search_and_validate(client, api_auth_token, search_request, expected_results)

    @pytest.mark.parametrize(
        "search_request, expected_results",
        [
            # Agency
            (get_search_request(agency_one_of=["not an agency"]), []),
            (
                get_search_request(agency_one_of=["NASA"]),
                [NASA_SPACE_FELLOWSHIP, NASA_INNOVATIONS, NASA_SUPERSONIC, NASA_K12_DIVERSITY],
            ),
            (get_search_request(agency_one_of=["LOC"]), [LOC_TEACHING, LOC_HIGHER_EDUCATION]),
            (get_search_request(agency_one_of=["DOS-ECA"]), [DOS_DIGITAL_LITERACY]),
            (get_search_request(agency_one_of=["DOC-EDA"]), [DOC_SPACE_COAST, DOC_MANUFACTURING]),
            (
                get_search_request(
                    agency_one_of=["DOC-EDA", "NASA", "LOC", "DOS-ECA", "something else"]
                ),
                OPPORTUNITIES,
            ),
            # Opportunity Status
            (
                get_search_request(opportunity_status_one_of=[OpportunityStatus.POSTED]),
                [NASA_SPACE_FELLOWSHIP, LOC_TEACHING, DOC_MANUFACTURING],
            ),
            (
                get_search_request(opportunity_status_one_of=[OpportunityStatus.FORECASTED]),
                [NASA_INNOVATIONS, LOC_HIGHER_EDUCATION],
            ),
            (
                get_search_request(opportunity_status_one_of=[OpportunityStatus.CLOSED]),
                [NASA_SUPERSONIC, DOS_DIGITAL_LITERACY],
            ),
            (
                get_search_request(opportunity_status_one_of=[OpportunityStatus.ARCHIVED]),
                [NASA_K12_DIVERSITY, DOC_SPACE_COAST],
            ),
            (
                get_search_request(
                    opportunity_status_one_of=[
                        OpportunityStatus.POSTED,
                        OpportunityStatus.FORECASTED,
                    ]
                ),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_INNOVATIONS,
                    LOC_TEACHING,
                    LOC_HIGHER_EDUCATION,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(
                    opportunity_status_one_of=[
                        OpportunityStatus.POSTED,
                        OpportunityStatus.FORECASTED,
                        OpportunityStatus.CLOSED,
                        OpportunityStatus.ARCHIVED,
                    ]
                ),
                OPPORTUNITIES,
            ),
            # Funding Instrument
            (
                get_search_request(
                    funding_instrument_one_of=[FundingInstrument.COOPERATIVE_AGREEMENT]
                ),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_K12_DIVERSITY,
                    LOC_TEACHING,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(funding_instrument_one_of=[FundingInstrument.GRANT]),
                [
                    NASA_INNOVATIONS,
                    NASA_SUPERSONIC,
                    LOC_HIGHER_EDUCATION,
                    DOC_SPACE_COAST,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(
                    funding_instrument_one_of=[FundingInstrument.PROCUREMENT_CONTRACT]
                ),
                [],
            ),
            (get_search_request(funding_instrument_one_of=[FundingInstrument.OTHER]), []),
            (
                get_search_request(
                    funding_instrument_one_of=[
                        FundingInstrument.COOPERATIVE_AGREEMENT,
                        FundingInstrument.GRANT,
                    ]
                ),
                OPPORTUNITIES,
            ),
            # Funding Category
            (
                get_search_request(funding_category_one_of=[FundingCategory.EDUCATION]),
                [NASA_SPACE_FELLOWSHIP, NASA_K12_DIVERSITY, LOC_TEACHING],
            ),
            (
                get_search_request(
                    funding_category_one_of=[
                        FundingCategory.SCIENCE_TECHNOLOGY_AND_OTHER_RESEARCH_AND_DEVELOPMENT
                    ]
                ),
                [NASA_INNOVATIONS, NASA_SUPERSONIC, DOC_MANUFACTURING],
            ),
            (
                get_search_request(funding_category_one_of=[FundingCategory.OTHER]),
                [LOC_HIGHER_EDUCATION, DOS_DIGITAL_LITERACY, DOC_SPACE_COAST],
            ),
            (
                get_search_request(funding_category_one_of=[FundingCategory.REGIONAL_DEVELOPMENT]),
                [DOC_SPACE_COAST],
            ),
            (
                get_search_request(
                    funding_category_one_of=[FundingCategory.EMPLOYMENT_LABOR_AND_TRAINING]
                ),
                [DOC_MANUFACTURING],
            ),
            (
                get_search_request(funding_category_one_of=[FundingCategory.ENERGY]),
                [DOC_MANUFACTURING],
            ),
            (get_search_request(funding_category_one_of=[FundingCategory.HOUSING]), []),
            (
                get_search_request(
                    funding_category_one_of=[
                        FundingCategory.SCIENCE_TECHNOLOGY_AND_OTHER_RESEARCH_AND_DEVELOPMENT,
                        FundingCategory.REGIONAL_DEVELOPMENT,
                    ]
                ),
                [NASA_INNOVATIONS, NASA_SUPERSONIC, DOC_SPACE_COAST, DOC_MANUFACTURING],
            ),
            # Applicant Type
            (
                get_search_request(applicant_type_one_of=[ApplicantType.OTHER]),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_INNOVATIONS,
                    NASA_K12_DIVERSITY,
                    DOS_DIGITAL_LITERACY,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(applicant_type_one_of=[ApplicantType.UNRESTRICTED]),
                [NASA_SUPERSONIC],
            ),
            (
                get_search_request(applicant_type_one_of=[ApplicantType.STATE_GOVERNMENTS]),
                [LOC_TEACHING, DOC_SPACE_COAST],
            ),
            (
                get_search_request(applicant_type_one_of=[ApplicantType.COUNTY_GOVERNMENTS]),
                [LOC_TEACHING, DOC_SPACE_COAST],
            ),
            (
                get_search_request(
                    applicant_type_one_of=[
                        ApplicantType.PUBLIC_AND_STATE_INSTITUTIONS_OF_HIGHER_EDUCATION
                    ]
                ),
                [LOC_HIGHER_EDUCATION, DOS_DIGITAL_LITERACY],
            ),
            (get_search_request(applicant_type_one_of=[ApplicantType.INDIVIDUALS]), []),
            (
                get_search_request(
                    applicant_type_one_of=[
                        ApplicantType.STATE_GOVERNMENTS,
                        ApplicantType.UNRESTRICTED,
                    ]
                ),
                [NASA_SUPERSONIC, LOC_TEACHING, DOC_SPACE_COAST],
            ),
            # Mix
            (
                get_search_request(
                    agency_one_of=["NASA"], applicant_type_one_of=[ApplicantType.OTHER]
                ),
                [NASA_SPACE_FELLOWSHIP, NASA_INNOVATIONS, NASA_K12_DIVERSITY],
            ),
            (
                get_search_request(
                    funding_instrument_one_of=[
                        FundingInstrument.GRANT,
                        FundingInstrument.PROCUREMENT_CONTRACT,
                    ],
                    funding_category_one_of=[
                        FundingCategory.SCIENCE_TECHNOLOGY_AND_OTHER_RESEARCH_AND_DEVELOPMENT
                    ],
                ),
                [NASA_INNOVATIONS, NASA_SUPERSONIC, DOC_MANUFACTURING],
            ),
            (
                get_search_request(
                    opportunity_status_one_of=[OpportunityStatus.POSTED],
                    applicant_type_one_of=[ApplicantType.OTHER],
                ),
                [NASA_SPACE_FELLOWSHIP, DOC_MANUFACTURING],
            ),
        ],
        ids=search_scenario_id_fnc,
    )
    def test_search_filters_200(self, client, api_auth_token, search_request, expected_results):
        call_search_and_validate(client, api_auth_token, search_request, expected_results)

    @pytest.mark.parametrize(
        "search_request, expected_results",
        [
            # Post date
            (
                get_search_request(
                    post_date={"start_date": "1970-01-01", "end_date": "2050-01-01"}
                ),
                OPPORTUNITIES,
            ),
            (
                get_search_request(
                    post_date={"start_date_relative": -20111, "end_date_relative": 9131}
                ),
                OPPORTUNITIES,
            ),
            (
                get_search_request(
                    post_date={"start_date": "1999-01-01", "end_date": "2000-01-01"}
                ),
                [],
            ),
            (
                get_search_request(
                    post_date={"start_date": "2015-01-01", "end_date": "2018-01-01"}
                ),
                [DOC_SPACE_COAST],
            ),
            (
                get_search_request(
                    post_date={"start_date": "2019-06-01", "end_date": "2024-01-01"}
                ),
                [NASA_SPACE_FELLOWSHIP, NASA_SUPERSONIC],
            ),
            (
                get_search_request(
                    post_date={"start_date_relative": -2063, "end_date_relative": -389}
                ),
                [NASA_SPACE_FELLOWSHIP, NASA_SUPERSONIC],
            ),
            (get_search_request(post_date={"end_date": "2016-01-01"}), [DOC_MANUFACTURING]),
            (get_search_request(post_date={"end_date_relative": -3310}), [DOC_MANUFACTURING]),
            # Close date
            (
                get_search_request(
                    close_date={"start_date": "1970-01-01", "end_date": "2050-01-01"}
                ),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_SUPERSONIC,
                    NASA_K12_DIVERSITY,
                    LOC_TEACHING,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(
                    close_date={"start_date_relative": -20111, "end_date_relative": 9131}
                ),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_SUPERSONIC,
                    NASA_K12_DIVERSITY,
                    LOC_TEACHING,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(close_date={"start_date": "2019-01-01"}),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_SUPERSONIC,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(close_date={"start_date_relative": -2214}),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_SUPERSONIC,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(close_date={"end_date": "2019-01-01"}),
                [NASA_K12_DIVERSITY, LOC_TEACHING],
            ),
            (
                get_search_request(close_date={"end_date_relative": -2214}),
                [NASA_K12_DIVERSITY, LOC_TEACHING],
            ),
            (
                get_search_request(
                    close_date={"start_date": "2015-01-01", "end_date": "2019-12-01"}
                ),
                [NASA_K12_DIVERSITY, DOC_SPACE_COAST],
            ),
            (
                get_search_request(
                    close_date={"start_date_relative": -3675, "end_date_relative": -1880}
                ),
                [NASA_K12_DIVERSITY, DOC_SPACE_COAST],
            ),
        ],
    )
    def test_search_filters_date_200(
        self, client, api_auth_token, search_request, expected_results
    ):
        call_search_and_validate(client, api_auth_token, search_request, expected_results)

    @pytest.mark.parametrize(
        "search_request, expected_results",
        [
            # Is cost sharing
            (get_search_request(is_cost_sharing_one_of=[True, False]), OPPORTUNITIES),
            (get_search_request(is_cost_sharing_one_of=["1", "0"]), OPPORTUNITIES),
            (
                get_search_request(is_cost_sharing_one_of=["t"]),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_SUPERSONIC,
                    LOC_TEACHING,
                    DOS_DIGITAL_LITERACY,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(is_cost_sharing_one_of=["on"]),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_SUPERSONIC,
                    LOC_TEACHING,
                    DOS_DIGITAL_LITERACY,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(is_cost_sharing_one_of=["false"]),
                [NASA_INNOVATIONS, NASA_K12_DIVERSITY, LOC_HIGHER_EDUCATION, DOC_SPACE_COAST],
            ),
            (
                get_search_request(is_cost_sharing_one_of=["no"]),
                [NASA_INNOVATIONS, NASA_K12_DIVERSITY, LOC_HIGHER_EDUCATION, DOC_SPACE_COAST],
            ),
        ],
    )
    def test_search_bool_filters_200(
        self, client, api_auth_token, search_request, expected_results
    ):
        call_search_and_validate(client, api_auth_token, search_request, expected_results)

    @pytest.mark.parametrize(
        "search_request, expected_results",
        [
            # Expected Number of Awards
            (
                get_search_request(expected_number_of_awards={"min": 0, "max": 1000}),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_INNOVATIONS,
                    NASA_SUPERSONIC,
                    LOC_TEACHING,
                    LOC_HIGHER_EDUCATION,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(expected_number_of_awards={"min": 5, "max": 10}),
                [NASA_SUPERSONIC],
            ),
            (
                get_search_request(expected_number_of_awards={"min": 12}),
                [LOC_TEACHING, DOC_SPACE_COAST, DOC_MANUFACTURING],
            ),
            (
                get_search_request(expected_number_of_awards={"min": 7}),
                [NASA_SUPERSONIC, LOC_TEACHING, DOC_SPACE_COAST, DOC_MANUFACTURING],
            ),
            # Award Floor
            (
                get_search_request(award_floor={"min": 0, "max": 10_000_000_000}),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_INNOVATIONS,
                    NASA_SUPERSONIC,
                    LOC_TEACHING,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(award_floor={"min": 1, "max": 5_000}),
                [
                    NASA_INNOVATIONS,
                    LOC_TEACHING,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                ],
            ),
            (
                get_search_request(award_floor={"min": 5_000, "max": 10_000}),
                [
                    NASA_INNOVATIONS,
                    NASA_SUPERSONIC,
                ],
            ),
            # Award Ceiling
            (
                get_search_request(award_ceiling={"min": 0, "max": 10_000_000_000}),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_INNOVATIONS,
                    NASA_SUPERSONIC,
                    LOC_TEACHING,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(award_ceiling={"min": 5_000, "max": 50_000}),
                [
                    NASA_INNOVATIONS,
                    NASA_SUPERSONIC,
                ],
            ),
            (
                get_search_request(award_ceiling={"min": 50_000}),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_SUPERSONIC,
                    DOC_MANUFACTURING,
                ],
            ),
            # Estimated Total Program Funding
            (
                get_search_request(
                    estimated_total_program_funding={"min": 0, "max": 100_000_000_000}
                ),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_INNOVATIONS,
                    LOC_TEACHING,
                    LOC_HIGHER_EDUCATION,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                    DOC_MANUFACTURING,
                ],
            ),
            (
                get_search_request(estimated_total_program_funding={"min": 0, "max": 5_000}),
                [
                    NASA_INNOVATIONS,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                ],
            ),
            # Mix
            (
                get_search_request(
                    expected_number_of_awards={"min": 0},
                    award_floor={"max": 10_000},
                    award_ceiling={"max": 10_000_000},
                    estimated_total_program_funding={"min": 10_000},
                ),
                [LOC_TEACHING],
            ),
            (
                get_search_request(
                    expected_number_of_awards={"max": 10},
                    award_floor={"min": 1_000, "max": 10_000},
                    award_ceiling={"max": 10_000_000},
                ),
                [NASA_INNOVATIONS, NASA_SUPERSONIC],
            ),
            (
                get_search_request(
                    expected_number_of_awards={"min": 1, "max": 2},
                    award_floor={"min": 0, "max": 1000},
                    award_ceiling={"min": 10000, "max": 10000000},
                    estimated_total_program_funding={"min": 123456, "max": 345678},
                ),
                [],
            ),
        ],
    )
    def test_search_int_filters_200(self, client, api_auth_token, search_request, expected_results):
        call_search_and_validate(client, api_auth_token, search_request, expected_results)

    @pytest.mark.parametrize(
        "search_request",
        [
            # Post Date
            (get_search_request(post_date={"start_date": "I am not a date"})),
            (get_search_request(post_date={"start_date": "123-456-789"})),
            (get_search_request(post_date={"start_date": "5"})),
            (get_search_request(post_date={"start_date": 5})),
            (get_search_request(post_date={"end_date": "I am not a date"})),
            (get_search_request(post_date={"end_date": "123-456-789"})),
            (get_search_request(post_date={"end_date": "5"})),
            (get_search_request(post_date={"end_date": 5})),
            # Close Date
            (get_search_request(close_date={"start_date": "I am not a date"})),
            (get_search_request(close_date={"start_date": "123-456-789"})),
            (get_search_request(close_date={"start_date": "5"})),
            (get_search_request(close_date={"start_date": 5})),
            (get_search_request(close_date={"end_date": "I am not a date"})),
            (get_search_request(close_date={"end_date": "123-456-789"})),
            (get_search_request(close_date={"end_date": "5"})),
            (get_search_request(close_date={"end_date": 5})),
        ],
    )
    def test_search_validate_date_filters_format_422(self, client, api_auth_token, search_request):
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )
        assert resp.status_code == 422

        json = resp.get_json()
        error = json["errors"][0]
        assert json["message"] == "Validation error"
        assert error["message"] == "Not a valid date."

    @pytest.mark.parametrize(
        "search_request",
        [
            # Post Date
            (get_search_request(post_date={"start_date": None, "end_date": None})),
            (
                get_search_request(
                    post_date={"start_date_relative": None, "end_date_relative": None}
                )
            ),
            (get_search_request(post_date={"start_date": None})),
            (get_search_request(post_date={"start_date_relative": None})),
            (get_search_request(post_date={"end_date": None})),
            (get_search_request(post_date={"end_date_relative": None})),
            (get_search_request(post_date={})),
            # Close Date
            (get_search_request(close_date={"start_date": None, "end_date": None})),
            (
                get_search_request(
                    close_date={"start_date_relative": None, "end_date_relative": None}
                )
            ),
            (get_search_request(close_date={"start_date": None})),
            (get_search_request(close_date={"start_date_relative": None})),
            (get_search_request(close_date={"end_date": None})),
            (get_search_request(close_date={"end_date_relative": None})),
            (get_search_request(close_date={})),
        ],
    )
    def test_search_validate_date_filters_nullability_422(
        self, client, api_auth_token, search_request
    ):
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )
        assert resp.status_code == 422

        json = resp.get_json()
        error = json["errors"][0]
        assert json["message"] == "Validation error"
        assert (
            error["message"]
            == "At least one of start_date/start_date_relative or end_date/end_date_relative must be provided."
        )

    @pytest.mark.parametrize(
        "search_request",
        [
            # Post Date
            (get_search_request(post_date={"start_date_relative": "I am not a relative date"})),
            (get_search_request(post_date={"start_date_relative": "2015-01-01"})),
            (get_search_request(post_date={"end_date_relative": "I am not a relative date"})),
            (get_search_request(post_date={"end_date_relative": "2015-01-01"})),
            # Close Date
            (get_search_request(close_date={"start_date_relative": "I am not a relative date"})),
            (get_search_request(close_date={"start_date_relative": "2015-01-01"})),
            (get_search_request(close_date={"end_date_relative": "I am not a relative date"})),
            (get_search_request(close_date={"end_date_relative": "2015-01-01"})),
        ],
    )
    def test_search_validate_date_relative_filters_format_422(
        self, client, api_auth_token, search_request
    ):
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )
        assert resp.status_code == 422

        json = resp.get_json()
        error = json["errors"][0]
        assert json["message"] == "Validation error"
        assert error["message"] == "Not a valid integer."

    @pytest.mark.parametrize(
        "search_request",
        [
            # post_date
            (get_search_request(post_date={"end_date_relative": 1000001})),
            (get_search_request(post_date={"end_date_relative": -1000001})),
            # close_date
            (get_search_request(close_date={"end_date_relative": 1000001})),
            (get_search_request(close_date={"end_date_relative": -1000001})),
        ],
    )
    def test_search_validate_date_relative_range_values_422(
        self, client, api_auth_token, search_request
    ):
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )

        json = resp.get_json()
        assert json["message"] == "Validation error"
        for error in json["errors"]:
            assert (
                error["message"]
                == "Must be greater than or equal to -1000000 and less than or equal to 1000000."
            )

    @pytest.mark.parametrize(
        "search_request",
        [
            # Post Date
            (get_search_request(post_date={"start_date": "2015-01-01", "end_date_relative": 15})),
            # Close Date
            (get_search_request(close_date={"start_date_relative": -4, "end_date": "2015-01-01"})),
        ],
    )
    def test_search_validate_date_filters_mix_format_422(
        self, client, api_auth_token, search_request
    ):
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )
        assert resp.status_code == 422

        json = resp.get_json()
        error = json["errors"][0]
        assert json["message"] == "Validation error"
        assert error["message"] == "Cannot have both absolute and relative date parameters."

    @pytest.mark.parametrize(
        "search_request",
        [
            get_search_request(assistance_listing_one_of=["12.345", "67.89"]),
            get_search_request(assistance_listing_one_of=["98.765"]),
            get_search_request(assistance_listing_one_of=["67.89", "54.24", "12.345", "86.753"]),
        ],
    )
    def test_search_validate_assistance_listing_filters_200(
            self, client, api_auth_token, search_request
    ):
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )
        assert resp.status_code == 200

    @pytest.mark.parametrize(
        "search_request",
        [
            get_search_request(assistance_listing_one_of=["12.345", "675.89"]),
            get_search_request(assistance_listing_one_of=["hello"]),
            get_search_request(assistance_listing_one_of=["67.89", "54.2412"]),
            get_search_request(assistance_listing_one_of=["1.1"]),
            get_search_request(assistance_listing_one_of=["12.hello"]),
            get_search_request(assistance_listing_one_of=["fourfive.sixseveneight"]),
            get_search_request(assistance_listing_one_of=["11..11"]),
        ],
    )
    def test_search_validate_assistance_listing_filters_422(
            self, client, api_auth_token, search_request
    ):
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )
        assert resp.status_code == 422

        json = resp.get_json()
        error = json["errors"][0]
        assert json["message"] == "Validation error"
        assert error["message"] == "String does not match expected pattern."

    @pytest.mark.parametrize(
        "search_request",
        [
            get_search_request(is_cost_sharing_one_of=["hello"]),
            get_search_request(is_cost_sharing_one_of=[True, "definitely"]),
            get_search_request(is_cost_sharing_one_of=[5, 6]),
            get_search_request(is_cost_sharing_one_of=["2024-01-01"]),
            get_search_request(is_cost_sharing_one_of=[{}]),
        ],
    )
    def test_search_validate_is_cost_sharing_filters_422(
            self, client, api_auth_token, search_request
    ):
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )
        assert resp.status_code == 422

        json = resp.get_json()
        error = json["errors"][0]
        assert json["message"] == "Validation error"
        assert error["message"] == "Not a valid boolean."

    @pytest.mark.parametrize(
        "search_request",
        [
            get_search_request(estimated_total_program_funding={"min": "hello", "max": "345678"}),
            get_search_request(award_floor={"min": "one"}),
            get_search_request(award_ceiling={"min": {}, "max": "123e4f5"}),
        ],
    )
    def test_search_validate_award_values_422(self, client, api_auth_token, search_request):
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )
        assert resp.status_code == 422

        json = resp.get_json()
        assert json["message"] == "Validation error"
        for error in json["errors"]:
            assert error["message"] == "Not a valid integer."

    @pytest.mark.parametrize(
        "search_request",
        [
            get_search_request(
                expected_number_of_awards={"min": -1},
                award_floor={"max": -2},
                award_ceiling={"max": "-10000000"},
                estimated_total_program_funding={"min": "-123456"},
            ),
            get_search_request(expected_number_of_awards={"min": -1, "max": 10000000}),
            get_search_request(
                estimated_total_program_funding={"max": "-5"}, award_floor={"max": "-9"}
            ),
        ],
    )
    def test_search_validate_award_values_negative_422(
            self, client, api_auth_token, search_request
    ):
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )

        json = resp.get_json()
        assert json["message"] == "Validation error"
        for error in json["errors"]:
            assert error["message"] == "Must be greater than or equal to 0."

    @pytest.mark.parametrize(
        "search_request",
        [
            # Both set to None
            get_search_request(
                expected_number_of_awards={"min": None, "max": None},
                award_floor={"min": None, "max": None},
                award_ceiling={"min": None, "max": None},
                estimated_total_program_funding={"min": None, "max": None},
            ),
            # Min only set
            get_search_request(
                expected_number_of_awards={"min": None},
                award_floor={"min": None},
                award_ceiling={"min": None},
                estimated_total_program_funding={"min": None},
            ),
            # Max only set
            get_search_request(
                expected_number_of_awards={"max": None},
                award_floor={"max": None},
                award_ceiling={"max": None},
                estimated_total_program_funding={"max": None},
            ),
        ],
    )
    def test_search_validate_award_values_nullability_422(
        self, client, api_auth_token, search_request
    ):
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )

        json = resp.get_json()
        assert json["message"] == "Validation error"
        for error in json["errors"]:
            assert error["message"] == "At least one of min or max must be provided."

    @pytest.mark.parametrize(
        "search_request, expected_results",
        [
            # Note that the sorting is not relevancy for this as we intend to update the relevancy scores a bit
            # and don't want to break this every time we adjust those.
            (
                get_search_request(
                    order_by="opportunity_id", sort_direction=SortDirection.ASCENDING, query="space"
                ),
                [
                    NASA_SPACE_FELLOWSHIP,
                    NASA_INNOVATIONS,
                    NASA_K12_DIVERSITY,
                    DOS_DIGITAL_LITERACY,
                    DOC_SPACE_COAST,
                ],
            ),
            (
                get_search_request(
                    order_by="opportunity_id",
                    sort_direction=SortDirection.ASCENDING,
                    query="43.008",
                ),
                [NASA_SPACE_FELLOWSHIP, NASA_K12_DIVERSITY, LOC_TEACHING],
            ),
            (
                get_search_request(
                    order_by="opportunity_id",
                    sort_direction=SortDirection.ASCENDING,
                    query="012ADV*",
                ),
                [LOC_TEACHING, LOC_HIGHER_EDUCATION],
            ),
            (
                get_search_request(
                    order_by="opportunity_id", sort_direction=SortDirection.ASCENDING, query="DOC*"
                ),
                [DOC_SPACE_COAST, DOC_MANUFACTURING],
            ),
            (
                get_search_request(
                    order_by="opportunity_id",
                    sort_direction=SortDirection.ASCENDING,
                    query="Aeronautics",
                ),
                [NASA_SUPERSONIC],
            ),
            (
                get_search_request(
                    order_by="opportunity_id",
                    sort_direction=SortDirection.ASCENDING,
                    query="literacy",
                ),
                [LOC_TEACHING, DOS_DIGITAL_LITERACY],
            ),
        ],
        ids=search_scenario_id_fnc,
    )
    def test_search_query_200(self, client, api_auth_token, search_request, expected_results):
        # This test isn't looking to validate opensearch behavior, just that we've connected fields properly and
        # results being returned are as expected.
        call_search_and_validate(client, api_auth_token, search_request, expected_results)

    def test_search_query_facets_200(self, client, api_auth_token):
        search_response = client.post(
            "/v1/opportunities/search",
            json=get_search_request(),
            headers={"X-Auth": api_auth_token},
        )

        assert search_response.status_code == 200
        facet_counts = search_response.get_json()["facet_counts"]
        assert facet_counts.keys() == {
            "agency",
            "applicant_type",
            "funding_instrument",
            "funding_category",
            "opportunity_status",
        }

    @pytest.mark.parametrize(
        "search_request",
        [
            # default scoring rule
            get_search_request(
                query="literacy",
            ),
            # agency scoring rule
            get_search_request(
                query="literacy",
                experimental={"scoring_rule": "agency"},
            ),
            # expanded scoring rule
            get_search_request(
                query="literacy",
                experimental={"scoring_rule": "expanded"},
            ),
        ],
    )
    def test_search_experimental_200(self, client, api_auth_token, search_request):
        # We are only testing for 200 responses when adding the experimental field into the request body.
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )
        assert resp.status_code == 200

        search_request["format"] = "csv"
        resp = client.post(
            "/v1/opportunities/search", json=search_request, headers={"X-Auth": api_auth_token}
        )
        assert resp.status_code == 200
