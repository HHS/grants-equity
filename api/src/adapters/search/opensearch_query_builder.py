import datetime
import typing

from src.pagination.pagination_models import SortDirection


class SearchQueryBuilder:
    """
    Utility to help build queries to OpenSearch

    This helps with making sure everything we want in a search query goes
    to the right spot in the large JSON object we're building. Note that
    it still requires some understanding of OpenSearch (eg. when to add ".keyword" to a field name)

    For example, if you wanted to build a query against a search index containing
    books with the following:
        * Page size of 5, page number 1
        * Sorted by relevancy score descending
        * Scored on titles containing "king"
        * Where the author is one of Brandon Sanderson or J R.R. Tolkien
        * With a page count between 300 and 1000
        * Returning aggregate counts of books by those authors in the full results

    This query could either be built manually and look like:

    {
      "size": 5,
      "from": 0,
      "track_scores": true,
      "sort": [
        {
          "_score": {
            "order": "desc"
          }
        }
      ],
      "query": {
        "bool": {
          "must": [
            {
              "simple_query_string": {
                "query": "king",
                "fields": [
                  "title.keyword"
                ],
                "default_operator": "AND"
              }
            }
          ],
          "filter": [
            {
              "terms": {
                "author.keyword": [
                  "Brandon Sanderson",
                  "J R.R. Tolkien"
                ]
              },
              "range": {
                "publication_date": {
                    "gte": 300,
                    "lte": 1000
                }
              }
            }
          ]
        }
      },
      "aggs": {
        "author": {
          "terms": {
            "field": "author.keyword",
            "size": 25,
            "min_doc_count": 0
          }
        }
      }
    }

    Or you could use the builder and produce the same result:

    search_query = SearchQueryBuilder()
                .pagination(page_size=5, page_number=1)
                .sort_by([("relevancy", SortDirection.DESCENDING)])
                .simple_query("king", fields=["title.keyword"])
                .filter_terms("author.keyword", terms=["Brandon Sanderson", "J R.R. Tolkien"])
                .filter_int_range("page_count", 300, 1000)
                .aggregation_terms(aggregation_name="author", field_name="author.keyword", minimum_count=0)
                .build()
    """

    def __init__(self) -> None:
        self.page_size = 25
        self.page_number = 1

        self.sort_values: list[dict[str, dict[str, str]]] = []

        self._track_total_hits: bool = True

        self.must: list[dict] = []
        self.filters: list[dict] = []

        self.aggregations: dict[str, dict] = {}

    def pagination(self, page_size: int, page_number: int) -> typing.Self:
        """
        Set the pagination for the search request.

        Note that page number should be the human-readable page number
        and start counting from 1.
        """
        self.page_size = page_size
        self.page_number = page_number
        return self

    def sort_by(self, sort_values: list[typing.Tuple[str, SortDirection]]) -> typing.Self:
        """
        List of tuples of field name + sort direction to sort by. If you wish to sort by the relevancy
        score provide a field name of "relevancy".

        The order of the tuples matters, and the earlier values will take precedence - or put another way
        the first tuple is the "primary sort", the second is the "secondary sort", and so on. If
        all of the primary sort values are unique, then the secondary sorts won't be relevant.

        If this method is not called, no sort info will be added to the request, and OpenSearch
        will internally default to sorting by relevancy score. If there is no scores calculated,
        then the order is likely the IDs of the documents in the index.

        Note that multiple calls to this method will erase any info provided in a prior call.
        """
        for field, sort_direction in sort_values:
            if field == "relevancy":
                field = "_score"

            self.sort_values.append({field: {"order": sort_direction.short_form()}})

        return self

    def track_total_hits(self, track_total_hits: bool) -> typing.Self:
        """
        Whether or not to track the total number of hits in the response accurately.

        By default OpenSearch will stop counting after 10k records are counted.
        """
        self._track_total_hits = track_total_hits
        return self

    def simple_query(self, query: str, fields: list[str]) -> typing.Self:
        """
        Adds a simple_query_string which queries against the provided fields.

        The fields must include the full path to the object, and can include optional suffixes
        to adjust the weighting. For example "opportunity_title^4" would increase any scores
        derived from that field by 4x.

        See: https://opensearch.org/docs/latest/query-dsl/full-text/simple-query-string/
        """
        self.must.append(
            {"simple_query_string": {"query": query, "fields": fields, "default_operator": "AND"}}
        )

        return self

    def filter_terms(self, field: str, terms: list) -> typing.Self:
        """
        For a given field, filter to a set of values.

        These filters do not affect the relevancy score, they are purely
        a binary filter on the overall results.
        """
        self.filters.append({"terms": {field: terms}})
        return self

    def filter_int_range(
        self, field: str, min_value: int | None, max_value: int | None
    ) -> typing.Self:
        """
        For a given field, filter results to a range of integer values.

        If min or max is not provided, the range is unbounded and only
        affects the minimum or maximum possible value. At least one min or max value must be specified.

        These filters do not affect the relevancy score, they are purely
        a binary filter on the overall results.
        """
        if min_value is None and max_value is None:
            raise ValueError("Cannot use int range filter if both min and max are None")

        range_filter = {}
        if min_value is not None:
            range_filter["gte"] = min_value
        if max_value is not None:
            range_filter["lte"] = max_value

        self.filters.append({"range": {field: range_filter}})
        return self

    def adjust_date_format(self, in_date: datetime.date | int | None) -> str:
        if in_date is None:
            return None
        if isinstance(in_date, int):
            return f"now{in_date:+}d"

        return in_date.isoformat()

    def filter_date_range(
        self,
        field: str,
        start_date: datetime.date| int | None,
        end_date: datetime.date | int| None
    ) -> typing.Self:
        """
        For a given field, filter results to a range of dates.

        If start or end is not provided, the range is unbounded and only
        affects the start or end date. At least one start or end date must be specified.

        These filters do not affect the relevancy score, they are purely
        a binary filter on the overall results.
        """
        if start_date is None and end_date is None:
            raise ValueError(
                "Cannot use date range filter if both start and end dates are None"
            )

        start_date_str = self.adjust_date_format(start_date)
        end_date_str = self.adjust_date_format(end_date)


        range_filter = {}
        if start_date_str is not None:
            range_filter["gte"] = start_date_str
        if end_date_str is not None:
            range_filter["lte"] = end_date_str

        self.filters.append({"range": {field: range_filter}})
        return self

    def aggregation_terms(
        self, aggregation_name: str, field_name: str, size: int = 25, minimum_count: int = 1
    ) -> typing.Self:
        """
        Add a term aggregation to the request. Aggregations are the counts of particular fields in the
        full response and are often displayed next to filters in a search UI.

        Size determines how many different values can be returned.
        Minimum count determines how many occurrences need to occur to include in the response.
            If you pass in 0 for this, then values that don't occur at all in the full result set will be returned.

        see: https://opensearch.org/docs/latest/aggregations/bucket/terms/
        """
        self.aggregations[aggregation_name] = {
            "terms": {"field": field_name, "size": size, "min_doc_count": minimum_count}
        }
        return self

    def build(self) -> dict:
        """
        Build the search request
        """

        # Base request
        page_offset = self.page_size * (self.page_number - 1)
        request: dict[str, typing.Any] = {
            "size": self.page_size,
            "from": page_offset,
            # Always include the scores in the response objects
            # even if we're sorting by non-relevancy
            "track_scores": True,
            "track_total_hits": self._track_total_hits,
        }

        # Add sorting if any was provided
        if len(self.sort_values) > 0:
            request["sort"] = self.sort_values

        # Add a bool query
        #
        # The "must" block contains anything relevant to scoring
        # The "filter" block contains filters that don't affect scoring and act
        #       as just binary filters
        #
        # See: https://opensearch.org/docs/latest/query-dsl/compound/bool/
        bool_query = {}
        if len(self.must) > 0:
            bool_query["must"] = self.must

        if len(self.filters) > 0:
            bool_query["filter"] = self.filters

        # Add the query object which wraps the bool query
        query_obj = {}
        if len(bool_query) > 0:
            query_obj["bool"] = bool_query

        if len(query_obj) > 0:
            request["query"] = query_obj

        # Add any aggregations
        # see: https://opensearch.org/docs/latest/aggregations/
        if len(self.aggregations) > 0:
            request["aggs"] = self.aggregations

        return request
