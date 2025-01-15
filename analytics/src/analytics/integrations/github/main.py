"""
Export data from GitHub.

TODO(widal001): 2025-01-04 Refactor and move this to src/analytics/etl/github when
we disable writing to disk in https://github.com/HHS/simpler-grants-gov/issues/3203
"""

import json
from datetime import datetime, timedelta
from pathlib import Path
from typing import Any

from analytics.integrations.github.client import GitHubGraphqlClient

PARENT_DIR = Path(__file__).resolve().parent


def safe_pluck(data: dict, keys: str) -> Any:  # noqa: ANN401
    """
    Safely pluck a value from a nested dictionary using a string of dot-separated keys.

    Example:
        data = {"content": {"parent": {"url": "example.com"}}}
        safe_pluck(data, "content.parent.url") # returns "example.com"
        safe_pluck(data, "content.missing") # returns None

    """
    current = data
    for key in keys.split("."):
        if not isinstance(current, dict) or key not in current:
            return None
        current = current[key]
    return current


def transform_project_data(
    raw_data: list[dict],
    owner: str,
    project: int,
    excluded_types: tuple = (),  # By default include everything
) -> list[dict]:
    """Pluck and reformat relevant fields for each item in the raw data."""
    return [
        {
            # project metadata
            "project_owner": owner,
            "project_number": project,
            # issue metadata
            "issue_title": safe_pluck(item, "content.title"),
            "issue_url": safe_pluck(item, "content.url"),
            "issue_parent": safe_pluck(item, "content.parent.url"),
            "issue_type": safe_pluck(item, "content.issueType.name"),
            "issue_status": safe_pluck(item, "status.name"),
            "issue_is_closed": safe_pluck(item, "content.closed"),
            "issue_opened_at": safe_pluck(item, "content.createdAt"),
            "issue_closed_at": safe_pluck(item, "content.closedAt"),
            "issue_points": safe_pluck(item, "points.number"),
            # sprint metadata
            "sprint_id": safe_pluck(item, "sprint.iterationId"),
            "sprint_name": safe_pluck(item, "sprint.title"),
            "sprint_start": safe_pluck(item, "sprint.startDate"),
            "sprint_length": safe_pluck(item, "sprint.duration"),
            "sprint_end": compute_end_date(
                safe_pluck(item, "sprint.startDate"),
                safe_pluck(item, "sprint.duration"),
            ),
            # roadmap metadata
            "deliverable_pillar": safe_pluck(item, "pillar.name"),
            "quad_id": safe_pluck(item, "quad.id"),
            "quad_name": safe_pluck(item, "quad.name"),
            "quad_start": safe_pluck(item, "quad.startDate"),
            "quad_length": safe_pluck(item, "quad.duration"),
            "quad_end": compute_end_date(
                safe_pluck(item, "quad.startDate"),
                safe_pluck(item, "quad.duration"),
            ),
        }
        for item in raw_data
        if safe_pluck(item, "content.issueType.name") not in excluded_types
    ]


def compute_end_date(start_date: str | None, duration: int | None) -> str | None:
    """Compute the end date based on start date and duration."""
    if not start_date or not duration:
        return None

    start = datetime.strptime(start_date, "%Y-%m-%d")  # noqa: DTZ007
    end = start + timedelta(days=duration)
    return end.strftime("%Y-%m-%d")


def export_sprint_data(
    client: GitHubGraphqlClient,
    owner: str,
    project: int,
    sprint_field: str,
    points_field: str,
    output_file: str,
) -> None:
    """Export the issue and project data from a Sprint Board."""
    # Load query
    query_path = PARENT_DIR / "getSprintData.graphql"
    with open(query_path) as f:
        query = f.read()

    # Set query variables
    variables = {
        "login": owner,
        "project": project,
        "sprintField": sprint_field,
        "pointsField": points_field,
    }

    # Execute query
    data = client.execute_paginated_query(
        query,
        variables,
        ["organization", "projectV2", "items"],
    )

    # Transform data
    # And exclude deliverables if they appear on the sprint boards
    # so that we use their status value from the roadmap board instead
    transformed_data = transform_project_data(
        raw_data=data,
        owner=owner,
        project=project,
        excluded_types=("Deliverable",),
    )

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transformed_data, f, indent=2)


def export_roadmap_data(
    client: GitHubGraphqlClient,
    owner: str,
    project: int,
    quad_field: str,
    pillar_field: str,
    output_file: str,
) -> None:
    """Export the issue and project data from a Roadmap Board."""
    # Load query
    query_path = PARENT_DIR / "getRoadmapData.graphql"
    with open(query_path) as f:
        query = f.read()

    # Set query variables
    variables = {
        "login": owner,
        "project": project,
        "quadField": quad_field,
        "pillarField": pillar_field,
    }

    # Execute query
    data = client.execute_paginated_query(
        query,
        variables,
        ["organization", "projectV2", "items"],
    )

    # Transform data
    transformed_data = transform_project_data(data, owner, project)

    # Write output
    with open(output_file, "w", encoding="utf-8") as f:
        json.dump(transformed_data, f, indent=2)
