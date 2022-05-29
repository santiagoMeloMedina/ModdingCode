from typing import Any, Dict
from modding.common import http, logging, aws_cli, settings
import requests
import json
import enum


class Role(enum.Enum):
    STUDENT = "STUDENT"
    EXPERT = "EXPERT"


class _Settings(settings.Settings):
    auth0_domain: str
    auth0_client_id: str
    auth0_client_secret: str
    auth0_audience: str
    expert_role_id: str
    student_role_id: str


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
    return dict(response.json()).get("access_token")


def assign_auth0_user_role(email: str, role_code: str, token: str) -> Dict[str, Any]:
    roles = {
        Role.EXPERT: _SETTINGS.expert_role_id,
        Role.STUDENT: _SETTINGS.student_role_id,
    }
    response = requests.post(
        f"https://{_SETTINGS.auth0_domain}/api/v2/roles/{roles.get(Role(role_code), str())}/users",
        data=json.dumps({"users": [email]}),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    return dict(response.json())


def create_auth0_user(email: str, password: str, token: str) -> Dict[str, Any]:
    response = requests.post(
        f"https://{_SETTINGS.auth0_domain}/api/v2/users",
        data=json.dumps(
            {
                "email": email,
                "connection": "Username-Password-Authentication",
                "password": password,
                "email_verified": True,
            }
        ),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
        },
    )
    return dict(response.json())


def verify_email_address(email: str) -> None:
    ses_client = aws_client.ses(email)
    ses_client.verify_address()
    _LOGGER.info("Email address %s verified" % (email))


def sign_up(email: str, password: str, role: str, **kwargs) -> Dict[str, Any]:
    result = {"message": f"Not verified email {email}"}
    auth0_token = get_auth0_access_token()
    creation_response = create_auth0_user(email, password, auth0_token)
    assign_auth0_user_role(email, role, auth0_token)
    if not ("statusCode" in creation_response and "error" in creation_response):
        verify_email_address(email=email)
        result = {"message": email}
    else:
        _LOGGER.error(creation_response.get("error"))
    return result
