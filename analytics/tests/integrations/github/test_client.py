"""Test the GitHubGraphqlClient class."""

from unittest.mock import Mock, patch

import pytest
from analytics.integrations.github.client import GitHubGraphqlClient, GraphqlError


@pytest.fixture(name="client")
def mock_client() -> GitHubGraphqlClient:
    """Fixture to initialize GitHubGraphqlClient with a mock token."""
    return GitHubGraphqlClient()


@pytest.fixture(name="sample_query")
def mock_query() -> str:
    """Fixture for a sample GraphQL query."""
    return """
    query($login: String!, $first: Int!, $after: String) {
      user(login: $login) {
        repositories(first: $first, after: $after) {
          pageInfo {
            hasNextPage
            endCursor
          }
          nodes {
            name
          }
        }
      }
    }
    """


@patch("requests.post")  # Mocks the requests.post() method
def test_paginated_query_success(
    mock_post: Mock,
    client: GitHubGraphqlClient,
    sample_query: str,
) -> None:
    """Test successfully making a paginated call and extracting data."""
    # Arrange - Mock the response from requests.post()
    mock_response = {
        "data": {
            "user": {
                "repositories": {
                    "nodes": [{"name": "repo1"}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            },
        },
    }
    mock_post.return_value = Mock(
        status_code=200,
        json=Mock(return_value=mock_response),
    )

    # Act - Set
    variables: dict[str, str] = {"login": "octocat"}
    path_to_nodes: list[str] = ["user", "repositories"]
    result: list[dict[str, str]] = client.execute_paginated_query(
        sample_query,
        variables,
        path_to_nodes,
    )

    assert result == [{"name": "repo1"}]


@patch("requests.post")
def test_invalid_path_to_nodes(
    mock_post: Mock,
    client: GitHubGraphqlClient,
    sample_query: str,
) -> None:
    """Test catching an error if the path_to_nodes is incorrect."""
    # Arrange - Mock the response from requests.post()
    mock_response = {
        "data": {
            "user": {
                "repositories": {
                    "nodes": [{"name": "repo1"}],
                    "pageInfo": {"hasNextPage": False, "endCursor": None},
                },
            },
        },
    }
    mock_post.return_value = Mock(
        status_code=200,
        json=Mock(return_value=mock_response),
    )

    # Arrange - Set variables and incorrect path to nodes
    variables: dict[str, str] = {"login": "octocat"}
    path_to_nodes: list[str] = ["user", "invalid_path"]

    # Assert - Check that the incorrect path raises a KeyError
    with pytest.raises(KeyError):
        client.execute_paginated_query(sample_query, variables, path_to_nodes)


@patch("requests.post")
def test_graphql_error(
    mock_post: Mock,
    client: GitHubGraphqlClient,
    sample_query: str,
) -> None:
    """Test raising a GraphqlError if errors are present in the response."""
    # Arrange - Mock the response from requests.post() to include an error
    mock_post.return_value = Mock(
        status_code=200,
        json=Mock(return_value={"errors": [{"message": "Test GitHub error"}]}),
    )

    # Arrange - Set the variables and path to nodes in the response body
    variables: dict[str, str] = {"login": "octocat"}
    path_to_nodes: list[str] = ["user", "repositories"]

    # Assert - Check that GraphqlError was raised
    with pytest.raises(GraphqlError) as excinfo:
        client.execute_paginated_query(sample_query, variables, path_to_nodes)

    # Assert - Check that it contains the error message from the mock response
    assert "Test GitHub error" in str(excinfo.value)
