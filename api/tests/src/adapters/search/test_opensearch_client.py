import uuid

import opensearchpy
import pytest

from src.adapters.search import get_opensearch_config
from src.adapters.search.opensearch_client import _get_connection_parameters

########################################################################
# These tests are primarily looking to validate
# that our wrappers around the OpenSearch client
# are being used correctly / account for error cases correctly.
#
# We are not validating all the intricacies of OpenSearch itself.
########################################################################


@pytest.fixture
def generic_index(search_client):
    # This is very similar to the opportunity_index fixture, but
    # is reused per unit test rather than a global value
    index_name = f"test-index-{uuid.uuid4().int}"

    search_client.create_index(index_name)

    try:
        yield index_name
    finally:
        # Try to clean up the index at the end
        search_client.delete_index(index_name)


def test_create_and_delete_index_duplicate(search_client):
    index_name = f"test-index-{uuid.uuid4().int}"

    search_client.create_index(index_name)
    with pytest.raises(Exception, match="already exists"):
        search_client.create_index(index_name)

    # Cleanup the index
    search_client.delete_index(index_name)
    with pytest.raises(Exception, match="no such index"):
        search_client.delete_index(index_name)


def test_bulk_upsert(search_client, generic_index):
    records = [
        {"id": 1, "title": "Green Eggs & Ham", "notes": "why are the eggs green?"},
        {"id": 2, "title": "The Cat in the Hat", "notes": "silly cat wears a hat"},
        {"id": 3, "title": "One Fish, Two Fish, Red Fish, Blue Fish", "notes": "fish"},
    ]

    search_client.bulk_upsert(generic_index, records, primary_key_field="id")
    # Verify the records are in the index
    for record in records:
        assert search_client._client.get(generic_index, record["id"])["_source"] == record

    # Can update + add more
    records = [
        {"id": 1, "title": "Green Eggs & Ham", "notes": "Sam, eat the eggs"},
        {"id": 2, "title": "The Cat in the Hat", "notes": "watch the movie"},
        {"id": 3, "title": "One Fish, Two Fish, Red Fish, Blue Fish", "notes": "colors & numbers"},
        {"id": 4, "title": "How the Grinch Stole Christmas", "notes": "who"},
    ]
    search_client.bulk_upsert(generic_index, records, primary_key_field="id")

    for record in records:
        assert search_client._client.get(generic_index, record["id"])["_source"] == record


def test_bulk_delete(search_client, generic_index):
    records = [
        {"id": 1, "title": "Green Eggs & Ham", "notes": "why are the eggs green?"},
        {"id": 2, "title": "The Cat in the Hat", "notes": "silly cat wears a hat"},
        {"id": 3, "title": "One Fish, Two Fish, Red Fish, Blue Fish", "notes": "fish"},
    ]

    search_client.bulk_upsert(generic_index, records, primary_key_field="id")

    search_client.bulk_delete(generic_index, [1])

    resp = search_client.search(generic_index, {}, include_scores=False)
    assert resp.records == records[1:]

    search_client.bulk_delete(generic_index, [2, 3])
    resp = search_client.search(generic_index, {}, include_scores=False)
    assert resp.records == []


def test_swap_alias_index(search_client, generic_index):
    alias_name = f"tmp-alias-{uuid.uuid4().int}"

    # Populate the generic index, we won't immediately use this one
    records = [
        {"id": 1, "data": "abc123"},
        {"id": 2, "data": "def456"},
        {"id": 3, "data": "xyz789"},
    ]
    search_client.bulk_upsert(generic_index, records, primary_key_field="id")

    # Create a different index that we'll attach to the alias first.
    tmp_index = f"test-tmp-index-{uuid.uuid4().int}"
    search_client.create_index(tmp_index)
    # Add a few records
    tmp_index_records = [
        {"id": 1, "data": "abc123"},
        {"id": 2, "data": "xyz789"},
    ]
    search_client.bulk_upsert(tmp_index, tmp_index_records, primary_key_field="id")

    # Set the alias
    search_client.swap_alias_index(tmp_index, alias_name)

    # Can search by this alias and get records from the tmp index
    resp = search_client.search(alias_name, {}, include_scores=False)
    assert resp.records == tmp_index_records

    # Swap the index to the generic one + delete the tmp one
    search_client.swap_alias_index(generic_index, alias_name)
    search_client.cleanup_old_indices("test-tmp-index", [generic_index])

    resp = search_client.search(alias_name, {}, include_scores=False)
    assert resp.records == records

    # Verify the tmp one was deleted
    assert search_client._client.indices.exists(tmp_index) is False


def test_index_or_alias_exists(search_client, generic_index):
    # Create a few aliased indexes
    index_a = f"test-index-a-{uuid.uuid4().int}"
    index_b = f"test-index-b-{uuid.uuid4().int}"
    index_c = f"test-index-c-{uuid.uuid4().int}"

    search_client.create_index(index_a)
    search_client.create_index(index_b)
    search_client.create_index(index_c)

    alias_index_a = f"test-alias-a-{uuid.uuid4().int}"
    alias_index_b = f"test-alias-b-{uuid.uuid4().int}"
    alias_index_c = f"test-alias-c-{uuid.uuid4().int}"

    search_client.swap_alias_index(index_a, alias_index_a)
    search_client.swap_alias_index(index_b, alias_index_b)
    search_client.swap_alias_index(index_c, alias_index_c)

    # Checking the indexes directly - we expect the index method to return true
    # and the alias method to not
    assert search_client.index_exists(index_a) is True
    assert search_client.index_exists(index_b) is True
    assert search_client.index_exists(index_c) is True

    assert search_client.alias_exists(index_a) is False
    assert search_client.alias_exists(index_b) is False
    assert search_client.alias_exists(index_c) is False

    # We just created these aliases, they should exist
    assert search_client.index_exists(alias_index_a) is True
    assert search_client.index_exists(alias_index_b) is True
    assert search_client.index_exists(alias_index_c) is True

    assert search_client.alias_exists(alias_index_a) is True
    assert search_client.alias_exists(alias_index_b) is True
    assert search_client.alias_exists(alias_index_c) is True

    # Other random things won't be found for either case
    assert search_client.index_exists("test-index-a") is False
    assert search_client.index_exists("asdasdasd") is False
    assert search_client.index_exists(alias_index_a + "-other") is False

    assert search_client.alias_exists("test-index-a") is False
    assert search_client.alias_exists("asdasdasd") is False
    assert search_client.alias_exists(alias_index_a + "-other") is False


def test_scroll(search_client, generic_index):
    records = [
        {"id": 1, "title": "Green Eggs & Ham", "notes": "why are the eggs green?"},
        {"id": 2, "title": "The Cat in the Hat", "notes": "silly cat wears a hat"},
        {"id": 3, "title": "One Fish, Two Fish, Red Fish, Blue Fish", "notes": "fish"},
        {"id": 4, "title": "Fox in Socks", "notes": "why he wearing socks?"},
        {"id": 5, "title": "The Lorax", "notes": "trees"},
        {"id": 6, "title": "Oh, the Places You'll Go", "notes": "graduation gift"},
        {"id": 7, "title": "Hop on Pop", "notes": "Let him sleep"},
        {"id": 8, "title": "How the Grinch Stole Christmas", "notes": "who"},
    ]

    search_client.bulk_upsert(generic_index, records, primary_key_field="id")

    results = []

    for response in search_client.scroll(generic_index, {"size": 3}):
        assert response.total_records == 8
        results.append(response)

    assert len(results) == 3
    assert len(results[0].records) == 3
    assert len(results[1].records) == 3
    assert len(results[2].records) == 2


def test_get_connection_parameters():
    # Just validating this builds as expected for local mode
    config = get_opensearch_config()
    params = _get_connection_parameters(config)

    # Mostly validating defaults get used
    assert params == {
        "hosts": [{"host": config.search_endpoint, "port": 9200}],
        "http_compress": True,
        "use_ssl": False,
        "verify_certs": False,
        "connection_class": opensearchpy.RequestsHttpConnection,
        "pool_maxsize": 10,
    }


def test_cleanup_old_indices(search_client):
    index_name_1 = f"test-index-{uuid.uuid4().int}"  # old index
    index_name_2 = f"test-index-{uuid.uuid4().int}"  # old index
    index_name_3 = f"partial-refresh-index-{uuid.uuid4().int}"  # old index
    index_name_4 = f"test-index-{uuid.uuid4().int}"  # new index

    search_client.create_index(index_name_1)
    search_client.create_index(index_name_2)
    search_client.create_index(index_name_3)
    search_client.create_index(index_name_4)

    # check all indexes were created
    assert search_client.index_exists(index_name_1) is True
    assert search_client.index_exists(index_name_2) is True
    assert search_client.index_exists(index_name_3) is True
    assert search_client.index_exists(index_name_4) is True

    # expect old index with same prefix to be deleted and others to remain
    search_client.cleanup_old_indices("test-index", [index_name_4])

    assert search_client.index_exists(index_name_1) is False
    assert search_client.index_exists(index_name_2) is False
    assert search_client.index_exists(index_name_3) is True
    assert search_client.index_exists(index_name_4) is True
