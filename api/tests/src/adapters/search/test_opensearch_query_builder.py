import uuid
from datetime import date

import pytest

from src.adapters.search.opensearch_query_builder import SearchQueryBuilder
from src.pagination.pagination_models import SortDirection
from tests.conftest import BaseTestClass

WAY_OF_KINGS = {
    "id": 1,
    "title": "The Way of Kings",
    "author": "Brandon Sanderson",
    "in_stock": True,
    "page_count": 1007,
    "publication_date": "2010-08-31",
}
WORDS_OF_RADIANCE = {
    "id": 2,
    "title": "Words of Radiance",
    "author": "Brandon Sanderson",
    "in_stock": False,
    "page_count": 1087,
    "publication_date": "2014-03-04",
}
OATHBRINGER = {
    "id": 3,
    "title": "Oathbringer",
    "author": "Brandon Sanderson",
    "in_stock": True,
    "page_count": 1248,
    "publication_date": "2017-11-14",
}
RHYTHM_OF_WAR = {
    "id": 4,
    "title": "Rhythm of War",
    "author": "Brandon Sanderson",
    "in_stock": False,
    "page_count": 1232,
    "publication_date": "2020-11-17",
}
GAME_OF_THRONES = {
    "id": 5,
    "title": "A Game of Thrones",
    "author": "George R.R. Martin",
    "in_stock": True,
    "page_count": 694,
    "publication_date": "1996-08-01",
}
CLASH_OF_KINGS = {
    "id": 6,
    "title": "A Clash of Kings",
    "author": "George R.R. Martin",
    "in_stock": True,
    "page_count": 768,
    "publication_date": "1998-11-16",
}
STORM_OF_SWORDS = {
    "id": 7,
    "title": "A Storm of Swords",
    "author": "George R.R. Martin",
    "in_stock": True,
    "page_count": 973,
    "publication_date": "2000-08-08",
}
FEAST_FOR_CROWS = {
    "id": 8,
    "title": "A Feast for Crows",
    "author": "George R.R. Martin",
    "in_stock": True,
    "page_count": 753,
    "publication_date": "2005-10-17",
}
DANCE_WITH_DRAGONS = {
    "id": 9,
    "title": "A Dance with Dragons",
    "author": "George R.R. Martin",
    "in_stock": False,
    "page_count": 1056,
    "publication_date": "2011-07-12",
}
FELLOWSHIP_OF_THE_RING = {
    "id": 10,
    "title": "The Fellowship of the Ring",
    "author": "J R.R. Tolkien",
    "in_stock": True,
    "page_count": 423,
    "publication_date": "1954-07-29",
}
TWO_TOWERS = {
    "id": 11,
    "title": "The Two Towers",
    "author": "J R.R. Tolkien",
    "in_stock": True,
    "page_count": 352,
    "publication_date": "1954-11-11",
}
RETURN_OF_THE_KING = {
    "id": 12,
    "title": "The Return of the King",
    "author": "J R.R. Tolkien",
    "in_stock": True,
    "page_count": 416,
    "publication_date": "1955-10-20",
}

FULL_DATA = [
    WAY_OF_KINGS,
    WORDS_OF_RADIANCE,
    OATHBRINGER,
    RHYTHM_OF_WAR,
    GAME_OF_THRONES,
    CLASH_OF_KINGS,
    STORM_OF_SWORDS,
    FEAST_FOR_CROWS,
    DANCE_WITH_DRAGONS,
    FELLOWSHIP_OF_THE_RING,
    TWO_TOWERS,
    RETURN_OF_THE_KING,
]


def validate_valid_request(
    search_client, index, request, expected_results, expected_aggregations=None
):
    json_value = request.build()
    try:
        resp = search_client.search(index, json_value, include_scores=False)

    except Exception:
        # If it errors while making the query, catch the exception just to give a message that makes it a bit clearer
        pytest.fail(
            f"Request generated was invalid and caused an error in search client: {json_value}"
        )

    assert (
        resp.records == expected_results
    ), f"{[record['title'] for record in resp.records]} != {[expected['title'] for expected in expected_results]}"

    if expected_aggregations is not None:
        assert resp.aggregations == expected_aggregations


class TestOpenSearchQueryBuilder(BaseTestClass):
    @pytest.fixture(scope="class")
    def search_index(self, search_client):
        index_name = f"test-search-index-{uuid.uuid4().int}"

        search_client.create_index(index_name)

        try:
            yield index_name
        finally:
            # Try to clean up the index at the end
            search_client.delete_index(index_name)

    @pytest.fixture(scope="class", autouse=True)
    def seed_data(self, search_client, search_index):
        search_client.bulk_upsert(search_index, FULL_DATA, primary_key_field="id")

    def test_query_builder_empty(self, search_client, search_index):
        builder = SearchQueryBuilder()

        assert builder.build() == {
            "size": 25,
            "from": 0,
            "track_scores": True,
            "track_total_hits": True,
        }

        validate_valid_request(search_client, search_index, builder, FULL_DATA)

    @pytest.mark.parametrize(
        "page_size,page_number,sort_values,expected_sort,expected_results",
        [
            ### ID Sorting
            (25, 1, [("id", SortDirection.ASCENDING)], [{"id": {"order": "asc"}}], FULL_DATA),
            (3, 1, [("id", SortDirection.ASCENDING)], [{"id": {"order": "asc"}}], FULL_DATA[:3]),
            (
                15,
                1,
                [("id", SortDirection.DESCENDING)],
                [{"id": {"order": "desc"}}],
                FULL_DATA[::-1],
            ),
            (
                5,
                2,
                [("id", SortDirection.DESCENDING)],
                [{"id": {"order": "desc"}}],
                FULL_DATA[-6:-11:-1],
            ),
            (10, 100, [("id", SortDirection.DESCENDING)], [{"id": {"order": "desc"}}], []),
            ### Title sorting
            (
                2,
                1,
                [("title.keyword", SortDirection.ASCENDING)],
                [{"title.keyword": {"order": "asc"}}],
                [CLASH_OF_KINGS, DANCE_WITH_DRAGONS],
            ),
            (
                3,
                4,
                [("title.keyword", SortDirection.DESCENDING)],
                [{"title.keyword": {"order": "desc"}}],
                [FEAST_FOR_CROWS, DANCE_WITH_DRAGONS, CLASH_OF_KINGS],
            ),
            (
                10,
                2,
                [("title.keyword", SortDirection.ASCENDING)],
                [{"title.keyword": {"order": "asc"}}],
                [WAY_OF_KINGS, WORDS_OF_RADIANCE],
            ),
            ### Page Count
            (
                3,
                1,
                [("page_count", SortDirection.ASCENDING)],
                [{"page_count": {"order": "asc"}}],
                [TWO_TOWERS, RETURN_OF_THE_KING, FELLOWSHIP_OF_THE_RING],
            ),
            (
                4,
                2,
                [("page_count", SortDirection.DESCENDING)],
                [{"page_count": {"order": "desc"}}],
                [WAY_OF_KINGS, STORM_OF_SWORDS, CLASH_OF_KINGS, FEAST_FOR_CROWS],
            ),
            ### Multi-sorts
            # Author ascending (Primary) + Page count descending (Secondary)
            (
                5,
                1,
                [
                    ("author.keyword", SortDirection.ASCENDING),
                    ("page_count", SortDirection.DESCENDING),
                ],
                [{"author.keyword": {"order": "asc"}}, {"page_count": {"order": "desc"}}],
                [OATHBRINGER, RHYTHM_OF_WAR, WORDS_OF_RADIANCE, WAY_OF_KINGS, DANCE_WITH_DRAGONS],
            ),
            # Author descending (Primary) + ID descending (Secondary)
            (
                4,
                1,
                [("author.keyword", SortDirection.DESCENDING), ("id", SortDirection.DESCENDING)],
                [{"author.keyword": {"order": "desc"}}, {"id": {"order": "desc"}}],
                [RETURN_OF_THE_KING, TWO_TOWERS, FELLOWSHIP_OF_THE_RING, DANCE_WITH_DRAGONS],
            ),
        ],
    )
    def test_query_builder_pagination_and_sorting(
        self,
        search_client,
        search_index,
        page_size,
        page_number,
        sort_values,
        expected_sort,
        expected_results,
    ):
        builder = (
            SearchQueryBuilder()
            .pagination(page_size=page_size, page_number=page_number)
            .sort_by(sort_values)
        )

        assert builder.build() == {
            "size": page_size,
            "from": page_size * (page_number - 1),
            "track_scores": True,
            "track_total_hits": True,
            "sort": expected_sort,
        }

        validate_valid_request(search_client, search_index, builder, expected_results)

    # Note that by having parametrize twice, it will run every one of the specific tests with the different
    # sort by parameter to show that they behave the same
    @pytest.mark.parametrize("sort_by", [[], [("relevancy", SortDirection.DESCENDING)]])
    @pytest.mark.parametrize(
        "filters,expected_results",
        [
            ### Author
            (
                [("author.keyword", ["Brandon Sanderson"])],
                [WAY_OF_KINGS, WORDS_OF_RADIANCE, OATHBRINGER, RHYTHM_OF_WAR],
            ),
            (
                [("author.keyword", ["George R.R. Martin", "Mark Twain"])],
                [
                    GAME_OF_THRONES,
                    CLASH_OF_KINGS,
                    STORM_OF_SWORDS,
                    FEAST_FOR_CROWS,
                    DANCE_WITH_DRAGONS,
                ],
            ),
            (
                [("author.keyword", ["J R.R. Tolkien"])],
                [FELLOWSHIP_OF_THE_RING, TWO_TOWERS, RETURN_OF_THE_KING],
            ),
            (
                [("author.keyword", ["Brandon Sanderson", "J R.R. Tolkien"])],
                [
                    WAY_OF_KINGS,
                    WORDS_OF_RADIANCE,
                    OATHBRINGER,
                    RHYTHM_OF_WAR,
                    FELLOWSHIP_OF_THE_RING,
                    TWO_TOWERS,
                    RETURN_OF_THE_KING,
                ],
            ),
            (
                [("author.keyword", ["Brandon Sanderson", "George R.R. Martin", "J R.R. Tolkien"])],
                FULL_DATA,
            ),
            ([("author.keyword", ["Mark Twain"])], []),
            ### in stock
            ([("in_stock", [False])], [WORDS_OF_RADIANCE, RHYTHM_OF_WAR, DANCE_WITH_DRAGONS]),
            ([("in_stock", [True, False])], FULL_DATA),
            ### page count
            ([("page_count", [1007, 694, 352])], [WAY_OF_KINGS, GAME_OF_THRONES, TWO_TOWERS]),
            ([("page_count", [1, 2, 3])], []),
            ### Multi-filter
            # Author + In Stock
            (
                [("author.keyword", ["Brandon Sanderson"]), ("in_stock", [True])],
                [WAY_OF_KINGS, OATHBRINGER],
            ),
            (
                [
                    ("author.keyword", ["George R.R. Martin", "J R.R. Tolkien"]),
                    ("in_stock", [False]),
                ],
                [DANCE_WITH_DRAGONS],
            ),
            # Author + Title
            (
                [
                    ("author.keyword", ["Brandon Sanderson", "J R.R. Tolkien", "Mark Twain"]),
                    (
                        "title.keyword",
                        ["A Game of Thrones", "The Way of Kings", "The Fellowship of the Ring"],
                    ),
                ],
                [WAY_OF_KINGS, FELLOWSHIP_OF_THE_RING],
            ),
            (
                [
                    ("author.keyword", ["George R.R. Martin", "J R.R. Tolkien"]),
                    (
                        "title.keyword",
                        ["A Game of Thrones", "The Way of Kings", "The Fellowship of the Ring"],
                    ),
                ],
                [GAME_OF_THRONES, FELLOWSHIP_OF_THE_RING],
            ),
        ],
    )
    def test_query_builder_filter_terms(
        self, search_client, search_index, filters, expected_results, sort_by
    ):
        builder = SearchQueryBuilder().sort_by(sort_by)

        expected_terms = []
        for filter in filters:
            builder.filter_terms(filter[0], filter[1])

            expected_terms.append({"terms": {filter[0]: filter[1]}})

        expected_query = {
            "size": 25,
            "from": 0,
            "track_scores": True,
            "track_total_hits": True,
            "query": {"bool": {"filter": expected_terms}},
        }

        if len(sort_by) > 0:
            expected_query["sort"] = [{"_score": {"order": "desc"}}]

        assert builder.build() == expected_query

        validate_valid_request(search_client, search_index, builder, expected_results)

    @pytest.mark.parametrize(
        "start_date,end_date,expected_results",
        [
            # Date range that will include all results
            # Absolute
            (date(1900, 1, 1), date(2050, 1, 1), FULL_DATA),
            # Relative
            (-45656, 9131, FULL_DATA),
            # Start only date range that will get all results
            # Absolute
            (date(1950, 1, 1), None, FULL_DATA),
            # Relative
            (-45656, None, FULL_DATA),
            # End only date range that will get all results
            # Absolute
            (None, date(2025, 1, 1), FULL_DATA),
            # Relative
            (None, 9131, FULL_DATA),
            # Range that filters to just oldest
            (
                date(1950, 1, 1),
                date(1960, 1, 1),
                [FELLOWSHIP_OF_THE_RING, TWO_TOWERS, RETURN_OF_THE_KING],
            ),
            # Unbounded range for oldest few
            (
                None,
                date(1990, 1, 1),
                [FELLOWSHIP_OF_THE_RING, TWO_TOWERS, RETURN_OF_THE_KING],
            ),
            # Unbounded range for newest few
            (date(2011, 8, 1), None, [WORDS_OF_RADIANCE, OATHBRINGER, RHYTHM_OF_WAR]),
            # Selecting a few in the middle
            (
                date(2005, 1, 1),
                date(2014, 1, 1),
                [WAY_OF_KINGS, FEAST_FOR_CROWS, DANCE_WITH_DRAGONS],
            ),
            # Exact date
            # Absolute
            (date(1954, 7, 29), date(1954, 7, 29), [FELLOWSHIP_OF_THE_RING]),
            # Relative
            ( -25747, -25747, []),
            # None fetched in range
            # Absolute
            (date(1981, 1, 1), date(1989, 1, 1), []),
            # Relative
            (-16093, -13171, []),
        ],
    )
    def test_query_builder_filter_date_range(
        self,
        search_client,
        search_index,
        start_date,
        end_date,
        expected_results,
    ):
        builder = (
            SearchQueryBuilder()
            .sort_by([])
            .filter_date_range(
                "publication_date", start_date, end_date
            )
        )

        expected_ranges={}
        if start_date is not None:
            expected_ranges["gte"] = f"now{start_date:+}d" if isinstance(start_date, int) else start_date.isoformat()
        if end_date is not None:
            expected_ranges["lte"] = f"now{end_date:+}d" if isinstance(end_date, int) else end_date.isoformat()

        expected_query = {
            "size": 25,
            "from": 0,
            "track_scores": True,
            "track_total_hits": True,
            "query": {"bool": {"filter": [{"range": {"publication_date": expected_ranges}}]}},
        }

        assert builder.build() == expected_query

        validate_valid_request(search_client, search_index, builder, expected_results)

    @pytest.mark.parametrize(
        "min_value,max_value,expected_results",
        [
            # All fetched
            (1, 2000, FULL_DATA),
            # None fetched
            (2000, 3000, []),
            # "Short" books
            (300, 700, [GAME_OF_THRONES, FELLOWSHIP_OF_THE_RING, TWO_TOWERS, RETURN_OF_THE_KING]),
            # Unbounded short
            (None, 416, [TWO_TOWERS, RETURN_OF_THE_KING]),
            # Unbounded long
            (1050, None, [WORDS_OF_RADIANCE, OATHBRINGER, RHYTHM_OF_WAR, DANCE_WITH_DRAGONS]),
            # Middle length
            (
                500,
                1010,
                [WAY_OF_KINGS, GAME_OF_THRONES, CLASH_OF_KINGS, STORM_OF_SWORDS, FEAST_FOR_CROWS],
            ),
        ],
    )
    def test_query_builder_filter_int_range(
        self, search_client, search_index, min_value, max_value, expected_results
    ):
        builder = (
            SearchQueryBuilder().sort_by([]).filter_int_range("page_count", min_value, max_value)
        )

        expected_ranges = {}
        if min_value is not None:
            expected_ranges["gte"] = min_value
        if max_value is not None:
            expected_ranges["lte"] = max_value

        expected_query = {
            "size": 25,
            "from": 0,
            "track_scores": True,
            "track_total_hits": True,
            "query": {"bool": {"filter": [{"range": {"page_count": expected_ranges}}]}},
        }

        assert builder.build() == expected_query

        validate_valid_request(search_client, search_index, builder, expected_results)

    def test_multiple_ranges(self, search_client, search_index):
        # Sanity test that we can specify multiple ranges (in this case, a date + int range)
        # in the same query
        builder = (
            SearchQueryBuilder()
            .sort_by([])
            .filter_int_range("page_count", 600, 1100)
            .filter_date_range("publication_date", date(2000, 1, 1), date(2013, 1, 1))
        )

        expected_results = [WAY_OF_KINGS, STORM_OF_SWORDS, FEAST_FOR_CROWS, DANCE_WITH_DRAGONS]
        validate_valid_request(
            search_client, search_index, builder, expected_results=expected_results
        )

    def test_filter_int_range_both_none(self):
        with pytest.raises(ValueError, match="Cannot use int range filter"):
            SearchQueryBuilder().filter_int_range("test_field", None, None)

    def test_filter_date_range_all_none(self):
        with pytest.raises(ValueError, match="Cannot use date range filter"):
            SearchQueryBuilder().filter_date_range("test_field", None, None)

    @pytest.mark.parametrize(
        "query,fields,expected_results,expected_aggregations",
        [
            (
                "king",
                ["title"],
                [WAY_OF_KINGS, CLASH_OF_KINGS, RETURN_OF_THE_KING],
                {
                    "author": {
                        "Brandon Sanderson": 1,
                        "George R.R. Martin": 1,
                        "J R.R. Tolkien": 1,
                    },
                    "in_stock": {0: 0, 1: 3},
                },
            ),
            (
                "R.R.",
                ["author"],
                [
                    GAME_OF_THRONES,
                    CLASH_OF_KINGS,
                    STORM_OF_SWORDS,
                    FEAST_FOR_CROWS,
                    DANCE_WITH_DRAGONS,
                    FELLOWSHIP_OF_THE_RING,
                    TWO_TOWERS,
                    RETURN_OF_THE_KING,
                ],
                {
                    "author": {
                        "Brandon Sanderson": 0,
                        "George R.R. Martin": 5,
                        "J R.R. Tolkien": 3,
                    },
                    "in_stock": {0: 1, 1: 7},
                },
            ),
            (
                "Martin (Crows | Storm)",
                ["title", "author"],
                [STORM_OF_SWORDS, FEAST_FOR_CROWS],
                {
                    "author": {
                        "Brandon Sanderson": 0,
                        "George R.R. Martin": 2,
                        "J R.R. Tolkien": 0,
                    },
                    "in_stock": {0: 0, 1: 2},
                },
            ),
            (
                "(Sanderson + (Words | King)) | Tolkien | Crow",
                ["title", "author"],
                [
                    WAY_OF_KINGS,
                    WORDS_OF_RADIANCE,
                    FEAST_FOR_CROWS,
                    FELLOWSHIP_OF_THE_RING,
                    TWO_TOWERS,
                    RETURN_OF_THE_KING,
                ],
                {
                    "author": {
                        "Brandon Sanderson": 2,
                        "George R.R. Martin": 1,
                        "J R.R. Tolkien": 3,
                    },
                    "in_stock": {0: 1, 1: 5},
                },
            ),
            (
                "-R.R. -Oathbringer",
                ["title", "author"],
                [WAY_OF_KINGS, WORDS_OF_RADIANCE, RHYTHM_OF_WAR],
                {
                    "author": {
                        "Brandon Sanderson": 3,
                        "George R.R. Martin": 0,
                        "J R.R. Tolkien": 0,
                    },
                    "in_stock": {0: 2, 1: 1},
                },
            ),
            (
                "Brandon | George | J",
                ["title", "author"],
                FULL_DATA,
                {
                    "author": {
                        "Brandon Sanderson": 4,
                        "George R.R. Martin": 5,
                        "J R.R. Tolkien": 3,
                    },
                    "in_stock": {0: 3, 1: 9},
                },
            ),
            (
                "how to make a pizza",
                ["title", "author"],
                [],
                {
                    "author": {
                        "Brandon Sanderson": 0,
                        "George R.R. Martin": 0,
                        "J R.R. Tolkien": 0,
                    },
                    "in_stock": {0: 0, 1: 0},
                },
            ),
        ],
    )
    def test_query_builder_simple_query_and_aggregations(
        self, search_client, search_index, query, fields, expected_results, expected_aggregations
    ):
        # Add a sort by ID ascending to make it so any relevancy from this is ignored, just testing that values returned
        builder = SearchQueryBuilder().sort_by([("id", SortDirection.ASCENDING)])

        builder.simple_query(query, fields)

        # Statically add the same aggregated fields every time
        builder.aggregation_terms("author", "author.keyword", minimum_count=0).aggregation_terms(
            "in_stock", "in_stock", minimum_count=0
        )

        assert builder.build() == {
            "size": 25,
            "from": 0,
            "track_scores": True,
            "track_total_hits": True,
            "query": {
                "bool": {
                    "must": [
                        {
                            "simple_query_string": {
                                "query": query,
                                "fields": fields,
                                "default_operator": "AND",
                            }
                        }
                    ]
                }
            },
            "sort": [{"id": {"order": "asc"}}],
            "aggs": {
                "author": {"terms": {"field": "author.keyword", "size": 25, "min_doc_count": 0}},
                "in_stock": {"terms": {"field": "in_stock", "size": 25, "min_doc_count": 0}},
            },
        }

        validate_valid_request(
            search_client, search_index, builder, expected_results, expected_aggregations
        )
