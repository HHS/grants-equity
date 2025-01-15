# pylint: disable=W0613,W0719,redefined-outer-name,broad-exception-caught
"""Test logging in general."""

import logging
import re

import pytest
from analytics.logs import formatters, init

from tests.assertions import assert_dict_contains


@pytest.fixture
def init_test_logger(caplog: pytest.LogCaptureFixture, monkeypatch: pytest.MonkeyPatch):
    """Fixture to setup a logger for tests."""
    caplog.set_level(logging.DEBUG)
    monkeypatch.setenv("LOG_FORMAT", "human-readable")
    with init("test_logging"):
        yield


@pytest.mark.parametrize(
    ("log_format", "expected_formatter"),
    [
        ("human-readable", formatters.HumanReadableFormatter),
        ("json", formatters.JsonFormatter),
    ],
)
def test_init(
    caplog: pytest.LogCaptureFixture,
    monkeypatch: pytest.MonkeyPatch,
    log_format: str,
    expected_formatter: logging.Formatter,
):
    """Test to verify behavior of initializing the logger."""
    caplog.set_level(logging.DEBUG)
    monkeypatch.setenv("LOG_FORMAT", log_format)

    with init("test_logging"):
        records = caplog.records
        assert len(records) == 2
        assert re.match(
            r"^start test_logging: \w+ [0-9.]+ \w+, hostname \S+, pid \d+, user \d+\([\w\.]+\)",
            records[0].message,
        )
        assert re.match(r"^invoked as:", records[1].message)

        formatter_types = [type(handler.formatter) for handler in logging.root.handlers]
        assert expected_formatter in formatter_types


def test_log_exception(
    init_test_logger: None,  # noqa: ARG001
    caplog: pytest.LogCaptureFixture,
):
    """Test to verify behavior of logging exceptions."""
    logger = logging.getLogger(__name__)

    try:
        msg = "example exception"
        raise Exception(msg)  # noqa: TRY301, TRY002
    except Exception:
        logger.exception(
            "test log message %s",
            "example_arg",
            extra={"key1": "value1", "key2": "value2"},
        )

    last_record: logging.LogRecord = caplog.records[-1]

    assert last_record.message == "test log message example_arg"
    assert last_record.funcName == "test_log_exception"
    assert last_record.threadName == "MainThread"
    assert last_record.exc_text.startswith("Traceback (most recent call last)")
    assert last_record.exc_text.endswith("Exception: example exception")
    assert last_record.__dict__["key1"] == "value1"
    assert last_record.__dict__["key2"] == "value2"


@pytest.mark.parametrize(
    ("args", "extra", "expected"),
    [
        pytest.param(
            ("ssn: 123456789",),
            None,
            {"message": "ssn: *********"},
            id="pii in msg",
        ),
        pytest.param(
            ("pii",),
            {"foo": "bar", "tin": "123456789", "dashed-ssn": "123-45-6789"},
            {
                "message": "pii",
                "foo": "bar",
                "tin": "*********",
                "dashed-ssn": "*********",
            },
            id="pii in extra",
        ),
        pytest.param(
            ("%s %s", "text", "123456789"),
            None,
            {"message": "text *********"},
            id="pii in interpolation args",
        ),
    ],
)
def test_mask_pii(
    init_test_logger: None,  # noqa: ARG001
    caplog: pytest.LogCaptureFixture,
    args: list,
    extra: dict,
    expected: dict,
):
    """Test to verify PII is masked properly in logs."""
    logger = logging.getLogger(__name__)

    logger.info(*args, extra=extra)

    assert len(caplog.records) == 1
    assert_dict_contains(caplog.records[0].__dict__, expected)
