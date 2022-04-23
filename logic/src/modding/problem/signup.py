from typing import Any, Dict
from modding.common import http, logging, aws_cli, settings
import requests


class _Settings(settings.Settings):
    auth0_domain: str
    auth0_client_id: str
    auth0_client_secret: str
    auth0_audience: str


_SETTINGS = _Settings()

_LOGGER = logging.Logger()

aws_client = aws_cli.AwsCustomClient


@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]):
    try:
        result = sign_up(**event.body)

        response = http.get_response(http.HttpCodes.SUCCESS, body=result)
    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()
    return response


def get_auth0_access_token() -> str:
    response = requests.post(
        f"https://{_SETTINGS.auth0_domain}/oauth/token",
        data={
            "grant_type": "client_credentials",
            "client_id": _SETTINGS.auth0_client_id,
            "client_secret": _SETTINGS.auth0_client_secret,
            "audience": _SETTINGS.auth0_audience,
        },
        headers={"Content-Type": "application/x-www-form-urlencoded"},
    )
    return dict(response.content).get("access_token")


def create_auth0_user(email: str, password: str) -> Dict[str, Any]:
    response = requests.post(
        f"https://{_SETTINGS.auth0_domain}/api/v2/users",
        data={
            "email": email,
            "connection": "Username-Password-Authentication",
            "password": password,
            "email_verified": True,
        },
        headers={"Authorization": f"Bearer {get_auth0_access_token()}"},
    )
    return dict(response.content)


def verify_email_address(email: str) -> None:
    ses_client = aws_client.ses(email)
    ses_client.verify_address()
    _LOGGER.info("Email address %s verified" % (email))


def sign_up(email: str, password: str, **kwargs) -> Dict[str, Any]:
    creation_response = create_auth0_user(email, password)
    if not ("statusCode" in creation_response and "error" in creation_response):
        verify_email_address(email=email)
    return {"verified": email}
