# pylint: disable=redefined-outer-name
"""
Configure pytest settings and create reusable fixtures and functions.

Visit pytest docs for more info:
https://docs.pytest.org/en/7.1.x/reference/fixtures.html
"""
import json
import logging
import uuid
from pathlib import Path

import _pytest.monkeypatch
import boto3
import moto
import pandas as pd
import pytest

from sqlalchemy import text  # isort: skip
from analytics.datasets.issues import IssueMetadata, IssueType
from analytics.integrations.etldb.etldb import EtlDb

logger = logging.getLogger(__name__)


# skips the integration tests in tests/integrations/
# to run the integration tests, invoke them directly: pytest tests/integrations/
collect_ignore = ["integrations"]

DAY_0 = "2023-10-31"
DAY_1 = "2023-11-01"
DAY_2 = "2023-11-02"
DAY_3 = "2023-11-03"
DAY_4 = "2023-11-04"
DAY_5 = "2023-11-05"

LABEL_30K = "deliverable: 30k ft"
LABEL_10K = "deliverable: 10k ft"


def pytest_addoption(parser: pytest.Parser):
    """Add a command line flag to collect tests that require a slack token."""
    parser.addoption(
        "--slack-token-set",
        action="store_true",
        default=False,
        help="Run tests that require a slack token",
    )


class MockSlackbot:
    """Create a mock slackbot issue for unit tests."""

    def upload_files_to_slack_channel(
        self,
        channel_id: str,
        files: list,
        message: str,
    ) -> None:
        """Stubs the corresponding method on the main SlackBot class."""
        assert isinstance(channel_id, str)
        print("Fake posting the following files to Slack with this message:")
        print(message)
        print(files)


@pytest.fixture(name="mock_slackbot")
def mock_slackbot_fixture():
    """Create a mock slackbot instance to stub post_to_slack() method."""
    return MockSlackbot()


def write_test_data_to_file(data: dict | list[dict], output_file: str | Path):
    """Write test JSON data to a file for use in a test."""
    parent_dir = Path(output_file).parent
    parent_dir.mkdir(exist_ok=True, parents=True)
    with open(output_file, "w", encoding="utf-8") as f:
        f.write(json.dumps(data, indent=2))


def json_issue_row(
    issue: int,
    labels: list[str] | None = None,
    created_at: str | None = "2023-11-01T00:00:00Z",
    closed_at: str | None = "2023-11-01T00:00:00Z",
) -> dict:
    """Generate a row of JSON issue data for testing."""
    new_labels = (
        [{"name": label, "id": hash(label)} for label in labels] if labels else []
    )
    return {
        "closedAt": closed_at,
        "createdAt": created_at,
        "number": issue,
        "labels": new_labels,
        "title": f"Issue {issue}",
    }


def json_roadmap_row(
    issue: int,
    deliverable: int,
    status: str = "In Progress",
    labels: list[str] | None = None,
) -> dict:
    """
    Generate a row of JSON roadmap data for testing.

    This is the format returned by the export_project_data() command
    """
    return {
        "assignees": ["mickeymouse"],
        "content": {
            "type": "Issue",
            "body": f"Description of test deliverable {issue}",
            "title": f"Deliverable {issue}",
            "number": issue,
            "repository": "HHS/simpler-grants-gov",
            "url": f"https://github.com/HHS/simpler-grants-gov/issues/{issue}",
        },
        "id": "PVTI_lADOABZxns4ASDf3zgJhmCk",
        "labels": labels or [LABEL_30K],
        "linked pull requests": [],
        "milestone": {
            "title": "Sample milestone",
            "description": "Deliverable for milestone",
            "dueOn": "2023-10-20T00:00:00Z",
        },
        "repository": "https://github.com/HHS/simpler-grants-gov",
        "status": status,
        "deliverable": f"Deliverable {deliverable}",
        "title": f"Deliverable {issue}",
    }


def json_sprint_row(
    issue: int,
    parent_number: int = -99,
    sprint_name: str = "Sprint 1",
    sprint_date: str = "2023-11-01",
    status: str = "Done",
    points: int = 5,
    deliverable: int = 1,
) -> dict:
    """
    Generate a row of JSON sprint data for testing.

    This is the format returned by the export_project_data() function.
    """
    return {
        "assignees": ["mickeymouse"],
        "content": {
            "type": "Issue",
            "body": f"Description of test issue {issue}",
            "title": f"Issue {issue}",
            "number": issue,
            "repository": "HHS/simpler-grants-gov",
            "url": f"https://github.com/HHS/simpler-grants-gov/issues/{issue}",
        },
        "id": "PVTI_lADOABZxns4ASDf3zgJhmCk",
        "labels": ["topic: infra", "project: grants.gov"],
        "linked pull requests": [],
        "milestone": {
            "title": "Sample milestone",
            "description": f"30k ft deliverable: #{parent_number}",
            "dueOn": "2023-10-20T00:00:00Z",
        },
        "repository": "https://github.com/HHS/simpler-grants-gov",
        "sprint": {"title": sprint_name, "startDate": sprint_date, "duration": 14},
        "status": status,
        "story Points": points,
        "deliverable": f"Deliverable {deliverable}",
        "title": f"Issue {issue}",
    }


def sprint_row(
    issue: int,
    created: str = DAY_1,
    closed: str | None = None,
    status: str = "In Progress",
    points: int | None = 1,
    sprint: int = 1,
    sprint_start: str = DAY_1,
    sprint_length: int = 2,
) -> dict:
    """Create a sample row of the SprintBoard dataset."""
    # create timestamp and time delta fields
    sprint_start_ts = pd.Timestamp(sprint_start)
    sprint_duration = pd.Timedelta(days=sprint_length)
    sprint_end_ts = sprint_start_ts + sprint_duration
    created_date = pd.Timestamp(created, tz="UTC")
    closed_date = pd.Timestamp(closed, tz="UTC") if closed else None
    # return the sample record
    return {
        "issue_number": issue,
        "issue_title": f"Issue {issue}",
        "type": "issue",
        "issue_body": f"Description of issue {issue}",
        "status": "Done" if closed else status,
        "assignees": "mickeymouse",
        "labels": [],
        "deliverable": "Deliverable 1",
        "url": f"https://github.com/HHS/simpler-grants-gov/issues/{issue}",
        "points": points,
        "milestone": "Milestone 1",
        "milestone_due_date": sprint_end_ts,
        "milestone_description": "Milestone 1 description",
        "sprint": f"Sprint {sprint}",
        "sprint_start_date": sprint_start_ts,
        "sprint_end_date": sprint_end_ts,
        "sprint_duration": sprint_duration,
        "created_date": created_date,
        "closed_date": closed_date,
    }


def issue(  # pylint: disable=too-many-locals
    issue: int,
    kind: IssueType = IssueType.TASK,
    owner: str = "HHS",
    project: int = 1,
    parent: str | None = None,
    points: int | None = 1,
    quad: str | None = None,
    epic: str | None = None,
    deliverable: str | None = None,
    sprint: int = 1,
    sprint_start: str = DAY_0,
    sprint_length: int = 2,
    created: str = DAY_0,
    closed: str | None = None,
) -> IssueMetadata:
    """Create a new issue."""
    # Create issue name
    name = f"{kind.value}{issue}"
    # Create sprint timestamp fields
    sprint_name = f"Sprint {sprint}"
    sprint_start_ts = pd.Timestamp(sprint_start)
    sprint_duration = pd.Timedelta(days=sprint_length)
    sprint_end_ts = sprint_start_ts + sprint_duration
    return IssueMetadata(
        # project metadata
        project_owner=owner,
        project_number=project,
        # issue metadata
        issue_title=name,
        issue_type=kind.value,
        issue_url=name,
        issue_is_closed=bool(closed),
        issue_opened_at=created,
        issue_closed_at=closed,
        issue_parent=parent,
        issue_points=points,
        # quad and epic metadata
        quad_name=quad,
        epic_title=epic,
        epic_url=epic,
        # deliverable metadata
        deliverable_title=deliverable,
        deliverable_url=deliverable,
        # sprint metadata
        sprint_id=sprint_name,
        sprint_name=sprint_name,
        sprint_start=sprint_start,
        sprint_end=sprint_end_ts.strftime("%Y-%m-%d"),
    )


####################
# AWS Mock Fixtures
####################


@pytest.fixture(autouse=True)
def reset_aws_env_vars(monkeypatch: pytest.MonkeyPatch) -> None:
    """
    Reset the aws env vars.

    This will prevent you from accidentally connecting
    to a real AWS account if you were doing some local testing.
    """
    monkeypatch.setenv("AWS_ACCESS_KEY_ID", "testing")
    monkeypatch.setenv("AWS_SECRET_ACCESS_KEY", "testing")
    monkeypatch.setenv("AWS_SECURITY_TOKEN", "testing")
    monkeypatch.setenv("AWS_SESSION_TOKEN", "testing")
    monkeypatch.setenv("AWS_DEFAULT_REGION", "us-east-1")


@pytest.fixture(autouse=True)
def use_cdn(monkeypatch: pytest.MonkeyPatch) -> None:
    """Set up CDN URL environment variable for tests."""
    monkeypatch.setenv("CDN_URL", "http://localhost:4566")


@pytest.fixture
def mock_s3() -> boto3.resource:
    """Instantiate an S3 bucket resource."""
    # https://docs.getmoto.org/en/stable/docs/configuration/index.html#whitelist-services
    with moto.mock_aws(config={"core": {"service_whitelist": ["s3"]}}):
        yield boto3.resource("s3")


@pytest.fixture
def mock_s3_bucket_resource(
    mock_s3: boto3.resource,
) -> boto3.resource("s3").Bucket:
    """Create and return a mock S3 bucket resource."""
    bucket = mock_s3.Bucket("test_bucket")
    bucket.create()
    return bucket


@pytest.fixture
def mock_s3_bucket(mock_s3_bucket_resource: boto3.resource("s3").Bucket) -> str:
    """Return name of mock S3 bucket."""
    return mock_s3_bucket_resource.name


# From https://github.com/pytest-dev/pytest/issues/363
@pytest.fixture(scope="session")
def monkeypatch_session() -> pytest.MonkeyPatch:
    """
    Create a monkeypatch instance.

    This can be used to monkeypatch global environment, objects, and attributes
    for the duration the test session.
    """
    mpatch = _pytest.monkeypatch.MonkeyPatch()
    yield mpatch
    mpatch.undo()


@pytest.fixture(scope="session")
def test_schema() -> str:
    """Create a unique test schema."""
    return f"test_schema_{uuid.uuid4().int}"


@pytest.fixture(scope="session")
def create_test_db(test_schema: str) -> EtlDb:
    """
    Create a temporary PostgreSQL schema.

    This function creates schema and a database engine
    that connects to that schema. Drops the schema after the context manager
    exits.
    """
    etldb_conn = EtlDb()

    with etldb_conn.connection() as conn:

        _create_schema(conn, test_schema)

        _create_opportunity_table(conn, test_schema)
        try:
            yield etldb_conn

        finally:
            _drop_schema(conn, test_schema)


def _create_schema(conn: EtlDb.connection, schema: str) -> None:
    """Create a database schema."""
    db_test_user = "app"

    with conn.begin():
        conn.execute(
            text(f"CREATE SCHEMA IF NOT EXISTS {schema} AUTHORIZATION {db_test_user};"),
        )
    logger.info("Created schema %s", schema)


def _drop_schema(conn: EtlDb.connection, schema: str) -> None:
    """Drop a database schema."""
    with conn.begin():
        conn.execute(text(f"DROP SCHEMA {schema} CASCADE;"))

    logger.info("Dropped schema %s", schema)


def _create_opportunity_table(conn: EtlDb.connection, schema: str) -> None:
    """Create opportunity tables."""
    with conn.begin():
        conn.execute(text(f"SET search_path TO {schema};"))
        # Get the path of the current file (test file)
        test_file_path = Path(__file__).resolve()

        # Construct the path to the SQL file
        sql_file_path = (
            test_file_path.parent.parent
            / "src"
            / "analytics"
            / "integrations"
            / "etldb"
            / "migrations"
            / "versions"
            / "0007_add_opportunity_tables.sql"
        )

        with open(sql_file_path) as file:
            create_table_commands = file.read()
            conn.execute(text(create_table_commands))

    logger.info("Created opportunity tables")
