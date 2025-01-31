import pytest

from src.constants.lookup_constants import FundingInstrument
from src.db.models.user_models import UserSavedSearch
from tests.src.api.opportunities_v1.conftest import get_search_request
from tests.src.db.models.factories import UserFactory


@pytest.fixture(autouse=True, scope="function")
def clear_saved_searches(db_session):
    db_session.query(UserSavedSearch).delete()
    db_session.commit()
    yield


def test_user_save_search_post_unauthorized_user(client, db_session, user, user_auth_token):
    # Try to save a search for a different user ID
    different_user = UserFactory.create()

    search_query = get_search_request(
        funding_instrument_one_of=[FundingInstrument.GRANT],
        agency_one_of=["LOC"],
    )

    response = client.post(
        f"/v1/users/{different_user.user_id}/saved-searches",
        headers={"X-SGG-Token": user_auth_token},
        json={"name": "Test Search", "search_query": search_query},
    )

    assert response.status_code == 401
    assert response.json["message"] == "Unauthorized user"

    # Verify no search was saved
    saved_searches = db_session.query(UserSavedSearch).all()
    assert len(saved_searches) == 0


def test_user_save_search_post_no_auth(client, db_session, user):
    search_query = get_search_request(
        funding_instrument_one_of=[FundingInstrument.GRANT],
        agency_one_of=["LOC"],
    )

    # Try to save a search without authentication
    response = client.post(
        f"/v1/users/{user.user_id}/saved-searches",
        json={"name": "Test Search", "search_query": search_query},
    )

    assert response.status_code == 401
    assert response.json["message"] == "Unable to process token"

    # Verify no search was saved
    saved_searches = db_session.query(UserSavedSearch).all()
    assert len(saved_searches) == 0


def test_user_save_search_post_invalid_request(client, user, user_auth_token, db_session):
    # Make request with missing required fields
    response = client.post(
        f"/v1/users/{user.user_id}/saved-searches",
        headers={"X-SGG-Token": user_auth_token},
        json={},
    )

    assert response.status_code == 422  # Validation error

    # Verify no search was saved
    saved_searches = db_session.query(UserSavedSearch).all()
    assert len(saved_searches) == 0


def test_user_save_search_post(client, user, user_auth_token, enable_factory_create, db_session):
    # Test data
    search_name = "Test Search"
    search_query = get_search_request(
        funding_instrument_one_of=[FundingInstrument.GRANT],
        agency_one_of=["LOC"],
    )

    # Make the request to save a search
    response = client.post(
        f"/v1/users/{user.user_id}/saved-searches",
        headers={"X-SGG-Token": user_auth_token},
        json={"name": search_name, "search_query": search_query},
    )

    assert response.status_code == 200
    assert response.json["message"] == "Success"

    # Verify the search was saved in the database
    saved_search = db_session.query(UserSavedSearch).one()
    assert saved_search.user_id == user.user_id
    assert saved_search.name == search_name
    assert saved_search.search_query == {
        "format": "json",
        "filters": {"agency": {"one_of": ["LOC"]}, "funding_instrument": {"one_of": ["grant"]}},
        "pagination": {
            "page_size": 25,
            "page_offset": 1,
            "sort_order": [
                {
                    "order_by": "opportunity_id",
                    "sort_direction": "ascending",
                }
            ],
        },
    }
