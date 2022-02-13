import copy
import json
from typing import Any
import pytest
import jwt

MOCK_API_GATEWAY_EVENT = {
    "resource": "/minicourse/category",
    "path": "/minicourse/category",
    "httpMethod": "POST",
    "headers": {"Accept": "*/*"},
    "body": '{\n    "name": "category1",\n    "description": "category description"\n}',
    "isBase64Encoded": False,
}

MOCK_USERNAME = "user1"
MOCK_TOKEN = jwt.encode({"username": MOCK_USERNAME}, "secret", algorithm="HS256")


@pytest.mark.disable_aws_mock
def test_apigateway_prehandler() -> None:
    from modding.common import aws_cli as subject

    @subject.AwsCustomClient.ApiGateway.pre_handler
    def mock(
        event: subject.AwsCustomClient.ApiGateway.AGWEvent, context: Any
    ) -> subject.AwsCustomClient.ApiGateway.AGWEvent:
        return event

    mock_parsed_event = subject.AwsCustomClient.ApiGateway.AGWEvent(
        body=json.loads(MOCK_API_GATEWAY_EVENT.get("body")),
        headers=MOCK_API_GATEWAY_EVENT.get("headers"),
    )

    parsed_event = mock(MOCK_API_GATEWAY_EVENT, {})

    assert parsed_event == mock_parsed_event


@pytest.mark.disable_aws_mock
def test_apigateway_prehandler_setting_username_on_repo() -> None:
    from modding.common import aws_cli as subject, repo
    from modding.utils import function

    mock_repo = repo.Repository("any", "any", "any")

    mock_event = {
        **MOCK_API_GATEWAY_EVENT,
        "headers": {
            **MOCK_API_GATEWAY_EVENT.get("headers"),
            "Authorization": f"Bearer {MOCK_TOKEN}",
        },
    }

    @function.decorator_builder(
        subject.AwsCustomClient.ApiGateway.include_repos_action, mock_repo
    )
    @subject.AwsCustomClient.ApiGateway.pre_handler
    def mock(event, context):
        pass

    mock(mock_event, {})

    assert mock_repo._username == MOCK_USERNAME
