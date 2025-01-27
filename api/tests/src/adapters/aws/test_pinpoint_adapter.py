from src.adapters.aws.pinpoint_adapter import _get_mock_responses, send_pinpoint_email_raw


def test_send_pinpoint_email_raw_with_mock():
    """Just a quick sanity check that the pinpoint mocking has a behavior we can use for other tests"""
    resp1 = send_pinpoint_email_raw(
        to_address="fake_mail1@fake.com",
        subject="email subject",
        message="this is an email",
        app_id="fake_app_id1",
    )
    resp2 = send_pinpoint_email_raw(
        to_address="fake_mail2@fake.com",
        subject="different subject",
        message="different email",
        app_id="fake_app_id2",
    )
    resp3 = send_pinpoint_email_raw(
        to_address="fake_mail3@fake.com",
        subject="another subject",
        message="another email",
        app_id="fake_app_id2",
    )
    mock_responses = _get_mock_responses()
    assert len(mock_responses) == 3

    req_resp1 = mock_responses[0]
    assert resp1 == req_resp1[1]
    req1 = req_resp1[0]
    assert req1["ApplicationId"] == "fake_app_id1"
    assert req1["MessageRequest"]["Addresses"] == {"fake_mail1@fake.com": {"ChannelType": "EMAIL"}}
    assert (
        req1["MessageRequest"]["MessageConfiguration"]["EmailMessage"]["SimpleEmail"]["Subject"][
            "Data"
        ]
        == "email subject"
    )
    assert (
        req1["MessageRequest"]["MessageConfiguration"]["EmailMessage"]["SimpleEmail"]["HtmlPart"][
            "Data"
        ]
        == "this is an email"
    )

    req_resp2 = mock_responses[1]
    assert resp2 == req_resp2[1]
    req2 = req_resp2[0]
    assert req2["ApplicationId"] == "fake_app_id2"
    assert req2["MessageRequest"]["Addresses"] == {"fake_mail2@fake.com": {"ChannelType": "EMAIL"}}
    assert (
        req2["MessageRequest"]["MessageConfiguration"]["EmailMessage"]["SimpleEmail"]["Subject"][
            "Data"
        ]
        == "different subject"
    )
    assert (
        req2["MessageRequest"]["MessageConfiguration"]["EmailMessage"]["SimpleEmail"]["HtmlPart"][
            "Data"
        ]
        == "different email"
    )

    req_resp3 = mock_responses[2]
    assert resp3 == req_resp3[1]
    req3 = req_resp3[0]
    assert req3["ApplicationId"] == "fake_app_id2"
    assert req3["MessageRequest"]["Addresses"] == {"fake_mail3@fake.com": {"ChannelType": "EMAIL"}}
    assert (
        req3["MessageRequest"]["MessageConfiguration"]["EmailMessage"]["SimpleEmail"]["Subject"][
            "Data"
        ]
        == "another subject"
    )
    assert (
        req3["MessageRequest"]["MessageConfiguration"]["EmailMessage"]["SimpleEmail"]["HtmlPart"][
            "Data"
        ]
        == "another email"
    )
