from typing import Any, Dict
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from modding.common import settings, logging


class _Settings(settings.Settings):
    signed_certificate: str
    api_audience: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

AUTHORIZATION_METHOD = "BEARER"


def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Any:
    try:
        auth_token = event.get("authorizationToken", "")
        method_arn = event.get("methodArn", "")

        if auth_token and method_arn:
            return get_policy(auth_token, method_arn)
        else:
            _LOGGER.error("No token or methodArn provided")
            raise Exception()

    except Exception as e:
        _LOGGER.error(e)
        raise Exception("Unauthorized")


def get_signed_pem() -> Any:
    signed_encoded = _SETTINGS.signed_certificate.encode()
    certificate = load_pem_x509_certificate(signed_encoded, default_backend())
    return certificate.public_key()


def jwt_verify(auth_token: str) -> str:
    public_key = get_signed_pem()
    payload = jwt.decode(
        auth_token, public_key, algorithms=["RS256"], audience=_SETTINGS.api_audience
    )
    return payload.get("sub", str())


def check_auth_and_get_token(auth_token: str) -> str:
    method_and_token = auth_token.split(" ")
    method, token = method_and_token[0], method_and_token[1]

    if token and method.upper() == AUTHORIZATION_METHOD:
        return token
    else:
        _LOGGER.error("Invalid auth value")
        raise Exception()


def generate_policy(principal_id: str, resource: str) -> Dict[str, Any]:
    return {
        "principalId": principal_id,
        "policyDocument": {
            "Version": "2012-10-17",
            "Statement": [
                {
                    "Action": "execute-api:Invoke",
                    "Effect": "Allow",
                    "Resource": resource,
                }
            ],
        },
    }


def get_policy(auth_token: str, method_arn: str) -> Dict[str, Any]:
    principal_id = jwt_verify(check_auth_and_get_token(auth_token))
    policy = generate_policy(principal_id, method_arn)
    return policy
