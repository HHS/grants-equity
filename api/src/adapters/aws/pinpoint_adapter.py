import logging
import uuid

import boto3
import botocore.client
from botocore.exceptions import ClientError
from pydantic import BaseModel, Field

from src.adapters.aws import get_boto_session
from src.adapters.aws.aws_session import is_local_aws

logger = logging.getLogger(__name__)

# An example of what the Pinpoint response looks like:
"""
{
    "ResponseMetadata": {
        "RequestId": "abcdef11-1111-2222-3333-4444abcabc",
        "HTTPStatusCode": 200,
        "HTTPHeaders": {
            # A bunch of generic HTTP/AWS headers
        },
        "RetryAttempts": 0
    },
    "MessageResponse": {
        "ApplicationId": "abc123",
        "RequestId": "ABCD-ASDASDASDAS",
        "Result": {
            "person@fake.com": {
                "DeliveryStatus": "SUCCESSFUL",
                "StatusCode": 200,
                "StatusMessage": "abcdef"
            }
        }
    }
}
"""


class PinpointResult(BaseModel):
    delivery_status: str = Field(alias="DeliveryStatus")
    status_code: int = Field(alias="StatusCode")
    status_message: str = Field(alias="StatusMessage")


class PinpointResponse(BaseModel):
    results: dict[str, PinpointResult] = Field(alias="Result", default_factory=dict)


def get_pinpoint_client(session: boto3.Session | None = None) -> botocore.client.BaseClient:
    if session is None:
        session = get_boto_session()

    return session.client("pinpoint")


def send_pinpoint_email_raw(
    to_address: str,
    subject: str,
    message: str,
    app_id: str,
    pinpoint_client: botocore.client.BaseClient | None = None,
) -> PinpointResponse:

    if pinpoint_client is None:
        pinpoint_client = get_pinpoint_client()

    # Based on: https://docs.aws.amazon.com/code-library/latest/ug/python_3_pinpoint_code_examples.html
    request = {
        "ApplicationId": app_id,
        "MessageRequest": {
            "Addresses": {to_address: {"ChannelType": "EMAIL"}},
            "MessageConfiguration": {
                "EmailMessage": {
                    # TODO - we'll switch this to use templates in the future
                    #        so keeping this simple with html/text the same
                    "SimpleEmail": {
                        "Subject": {"Charset": "UTF-8", "Data": subject},
                        "HtmlPart": {"Charset": "UTF-8", "Data": message},
                        "TextPart": {"Charset": "UTF-8", "Data": message},
                    }
                }
            },
        },
    }
    # If we are running locally (or in unit tests), don't actually query
    # AWS - unlike our other AWS integrations, there is no mocking support yet
    # for Pinpoint, so we built something ourselves that also works when run locally
    if is_local_aws():
        return _handle_mock_response(request, to_address)

    try:
        raw_response = pinpoint_client.send_messages(**request)
    except ClientError:
        logger.exception("Failed to send email")
        raise

    return PinpointResponse.model_validate(raw_response["MessageResponse"])


_mock_responses: list[tuple[dict, PinpointResponse]] = []


def _handle_mock_response(request: dict, to_address: str) -> PinpointResponse:
    # By default, return a response that roughly looks like a real success
    response = PinpointResponse(
        Result={
            to_address: PinpointResult(
                DeliveryStatus="SUCCESSFUL", StatusCode=200, StatusMessage=str(uuid.uuid4())
            )
        }
    )
    global _mock_responses
    _mock_responses.append((request, response))

    return response


def _get_mock_responses() -> list[tuple[dict, PinpointResponse]]:
    return _mock_responses
