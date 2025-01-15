import logging
from typing import Any, Generator, Iterable

import opensearchpy

from src.adapters.search.opensearch_config import OpensearchConfig, get_opensearch_config
from src.adapters.search.opensearch_response import SearchResponse

logger = logging.getLogger(__name__)

# By default, we'll override the default analyzer+tokenization
# for a search index. You can provide your own when calling create_index
DEFAULT_INDEX_ANALYSIS = {
    "analyzer": {
        "default": {
            "type": "custom",
            "filter": ["lowercase", "custom_stemmer"],
            "tokenizer": "standard",
        }
    },
    # Change the default stemming to use snowball which handles plural
    # queries better than the default
    # TODO - there are a lot of stemmers, we should take some time to figure out
    #        which one works best with our particular dataset. Snowball is really
    #        basic and naive (literally just adjusting suffixes on words in common patterns)
    #        which might be fine generally, but we work with a lot of acronyms
    #        and should verify that doesn't cause any issues.
    # see: https://opensearch.org/docs/latest/analyzers/token-filters/index/
    "filter": {"custom_stemmer": {"type": "snowball", "name": "english"}},
}


class SearchClient:
    def __init__(self, opensearch_config: OpensearchConfig | None = None) -> None:
        if opensearch_config is None:
            opensearch_config = get_opensearch_config()

        # See: https://opensearch.org/docs/latest/clients/python-low-level/ for more details
        self._client = opensearchpy.OpenSearch(**_get_connection_parameters(opensearch_config))

    def create_index(
        self,
        index_name: str,
        *,
        shard_count: int = 1,
        replica_count: int = 1,
        analysis: dict | None = None,
    ) -> None:
        """
        Create an empty search index
        """

        # Allow the user to adjust how the index analyzer + tokenization works
        # but also have a general default.
        if analysis is None:
            analysis = DEFAULT_INDEX_ANALYSIS

        body = {
            "settings": {
                "index": {"number_of_shards": shard_count, "number_of_replicas": replica_count},
                "analysis": analysis,
            },
        }

        logger.info("Creating search index %s", index_name, extra={"index_name": index_name})
        self._client.indices.create(index_name, body=body)

    def delete_index(self, index_name: str) -> None:
        """
        Delete an index. Can also delete all indexes via a prefix.
        """
        logger.info("Deleting search index %s", index_name, extra={"index_name": index_name})
        self._client.indices.delete(index=index_name)

    def put_pipeline(self, pipeline: dict, pipeline_name: str) -> None:
        """
        Create a pipeline
        """
        resp = self._client.ingest.put_pipeline(id=pipeline_name, body=pipeline)
        if resp["acknowledged"]:
            logger.info(f"Pipeline '{pipeline_name}' created successfully!")
        else:
            status_code = resp["status"] or 500
            error_message = resp["error"]["reason"] or "Internal Server Error"

            raise Exception(
                f"Failed to create pipeline {pipeline_name}: {error_message}. Status code: {status_code}"
            )

    def bulk_upsert(
        self,
        index_name: str,
        records: Iterable[dict[str, Any]],
        primary_key_field: str,
        *,
        refresh: bool = True,
        pipeline: str | None = None,
    ) -> None:
        """
        Bulk upsert records to an index

        See: https://opensearch.org/docs/latest/api-reference/document-apis/bulk/ for details
        In this method we only use the "index" operation which creates or updates a record
        based on the id value.
        """

        bulk_operations = []

        for record in records:
            # For each record, we create two entries in the bulk operation list
            # which include the unique ID + the actual record on separate lines
            # When this is sent to the search index, this will send two lines like:
            #
            # {"index": {"_id": 123}}
            # {"opportunity_id": 123, "opportunity_title": "example title", ...}
            bulk_operations.append({"index": {"_id": record[primary_key_field]}})
            bulk_operations.append(record)

        logger.info(
            "Upserting records to %s",
            index_name,
            extra={
                "index_name": index_name,
                "record_count": int(len(bulk_operations) / 2),
                "operation": "update",
            },
        )
        bulk_args = {"index": index_name, "body": bulk_operations, "refresh": refresh}
        if pipeline:
            bulk_args["pipeline"] = pipeline

        self._client.bulk(**bulk_args)

    def bulk_delete(self, index_name: str, ids: Iterable[Any], *, refresh: bool = True) -> None:
        """
        Bulk delete records from an index

        See: https://opensearch.org/docs/latest/api-reference/document-apis/bulk/ for details.
        In this method, we delete records based on the IDs passed in.
        """
        bulk_operations = []

        for _id in ids:
            # { "delete": { "_id": "tt2229499" } }
            bulk_operations.append({"delete": {"_id": _id}})

        logger.info(
            "Deleting records from %s",
            index_name,
            extra={
                "index_name": index_name,
                "record_count": len(bulk_operations),
                "operation": "delete",
            },
        )
        self._client.bulk(index=index_name, body=bulk_operations, refresh=refresh)

    def index_exists(self, index_name: str) -> bool:
        """
        Check if an index OR alias exists by a given name
        """
        return self._client.indices.exists(index_name)

    def alias_exists(self, alias_name: str) -> bool:
        """
        Check if an alias exists
        """
        existing_index_mapping = self._client.cat.aliases(alias_name, format="json")
        return len(existing_index_mapping) > 0

    def cleanup_old_indices(self, index_prefix: str, indexes_to_keep: list[str]) -> None:
        """
        Cleanup old indexes now that they aren't connected to the alias
        """
        resp = self._client.cat.indices(f"{index_prefix}-*", format="json", h=["index"])

        old_indexes = [
            index["index"] for index in resp if index["index"] not in indexes_to_keep
        ]  # omit the newly created one

        for index in old_indexes:
            self.delete_index(index)

    def swap_alias_index(self, index_name: str, alias_name: str) -> None:
        """
        For a given index, set it to the given alias. If any existing index(es) are
        attached to the alias, remove them from the alias.

        This operation is done atomically.
        """
        extra = {"index_name": index_name, "index_alias": alias_name}
        logger.info("Swapping index that backs alias %s", alias_name, extra=extra)

        existing_index_mapping = self._client.cat.aliases(alias_name, format="json")
        existing_indexes = [i["index"] for i in existing_index_mapping]

        logger.info(
            "Found existing indexes", extra=extra | {"existing_indexes": ",".join(existing_indexes)}
        )

        actions = [{"add": {"index": index_name, "alias": alias_name}}]

        for index in existing_indexes:
            actions.append({"remove": {"index": index, "alias": alias_name}})

        self._client.indices.update_aliases({"actions": actions})

    def search_raw(self, index_name: str, search_query: dict) -> dict:
        # Simple wrapper around search if you don't want the request or response
        # object handled in any special way.
        return self._client.search(index=index_name, body=search_query)

    def search(
        self,
        index_name: str,
        search_query: dict,
        include_scores: bool = True,
        params: dict | None = None,
    ) -> SearchResponse:
        if params is None:
            params = {}

        response = self._client.search(index=index_name, body=search_query, params=params)
        return SearchResponse.from_opensearch_response(response, include_scores)

    def scroll(
        self,
        index_name: str,
        search_query: dict,
        include_scores: bool = True,
        duration: str = "10m",
    ) -> Generator[SearchResponse, None, None]:
        """
        Scroll (iterate) over a large result set a given search query.

        This query uses additional resources to keep the response open, but
        keeps a consistent set of results and is useful for backend processes
        that need to fetch a large amount of search data. After processing the results,
        the scroll lock is closed for you.

        This method is setup as a generator method and the results can be iterated over::

            for response in search_client.scroll("my_index", {"size": 10000}):
                for record in response.records:
                    process_record(record)


        See: https://opensearch.org/docs/latest/api-reference/scroll/
        """

        # start scroll
        response = self.search(
            index_name=index_name,
            search_query=search_query,
            include_scores=include_scores,
            params={"scroll": duration},
        )
        scroll_id = response.scroll_id

        yield response

        # iterate
        while True:
            raw_response = self._client.scroll({"scroll_id": scroll_id, "scroll": duration})
            response = SearchResponse.from_opensearch_response(raw_response, include_scores)

            # The scroll ID can change between queries according to the docs, so we
            # keep updating the value while iterating in case they change.
            scroll_id = response.scroll_id

            if len(response.records) == 0:
                break

            yield response

        # close scroll
        self._client.clear_scroll(scroll_id=scroll_id)


def _get_connection_parameters(opensearch_config: OpensearchConfig) -> dict[str, Any]:
    # See: https://opensearch.org/docs/latest/clients/python-low-level/#connecting-to-opensearch
    # for further details on configuring the connection to OpenSearch
    params = dict(
        hosts=[{"host": opensearch_config.search_endpoint, "port": opensearch_config.search_port}],
        http_compress=True,
        use_ssl=opensearch_config.search_use_ssl,
        verify_certs=opensearch_config.search_verify_certs,
        connection_class=opensearchpy.RequestsHttpConnection,
        pool_maxsize=opensearch_config.search_connection_pool_size,
    )

    # We'll assume if the aws_region is set, we're running in AWS
    # and should connect using the session credentials
    if opensearch_config.aws_region:
        # Get credentials and authorize with AWS Opensearch Serverless (es)
        # TODO - once we have the user setup in Opensearch, we want to change to this approach
        # credentials = boto3.Session().get_credentials()
        # auth = opensearchpy.AWSV4SignerAuth(credentials, opensearch_config.aws_region, "es")
        auth = (opensearch_config.search_username, opensearch_config.search_password)
        params["http_auth"] = auth

    return params
