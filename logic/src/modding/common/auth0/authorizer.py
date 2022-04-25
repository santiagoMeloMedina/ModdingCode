from typing import Any, Dict, List, Tuple
import jwt
from cryptography.hazmat.backends import default_backend
from cryptography.x509 import load_pem_x509_certificate
from modding.common import settings, logging


class _Settings(settings.Settings):
    signed_certificate: str
    api_audience: str
    authorizer_roles: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

AUTHORIZATION_METHOD = "BEARER"
AUTH0_SCOPES_PARAM = "permissions"


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


def _method_to_segments(method: str) -> List[str]:
    return method.split("/")


def _get_authorizer_method_arn_and_scopes() -> List[Tuple[List[str], List[str]]]:
    result = []
    if not _SETTINGS.authorizer_roles == "empty":
        methods = _SETTINGS.authorizer_roles.split(" ")
        for method_scopes in methods:
            parts = method_scopes.split(":")
            if len(parts) == 2:
                method, scopes = parts[0], parts[1].split(",")
                result.append((_method_to_segments(method), scopes))

    return result


def _all_segments_match(method_segments: List[str], lambda_segments: List[str]) -> bool:
    result = False
    trimmed_method = method_segments[-len(lambda_segments) :]
    if len(trimmed_method) == len(lambda_segments):
        result = trimmed_method == lambda_segments

    return result


def _check_roles(method_arn: str, token_scopes: List[str]) -> None:
    scopes = set(token_scopes)
    lambdas_scopes = _get_authorizer_method_arn_and_scopes()

    method_segments = _method_to_segments(method_arn)
    for lambda_scopes in lambdas_scopes:
        lambda_segments, lambda_scopes = lambda_scopes
        if _all_segments_match(method_segments, lambda_segments):
            for scope in lambda_scopes:
                if scope not in scopes:
                    raise Exception("Does not have required scopes")

            return None


def get_signed_pem() -> Any:
    signed_encoded = _SETTINGS.signed_certificate.encode()
    certificate = load_pem_x509_certificate(signed_encoded, default_backend())
    return certificate.public_key()


def jwt_verify(auth_token: str, method_arn: str) -> str:
    public_key = get_signed_pem()
    payload = jwt.decode(
        auth_token, public_key, algorithms=["RS256"], audience=_SETTINGS.api_audience
    )

    scopes = payload.get(AUTH0_SCOPES_PARAM, list())
    _check_roles(method_arn, scopes)

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
                    "Resource": "*",
                }
            ],
        },
    }


def get_policy(auth_token: str, method_arn: str) -> Dict[str, Any]:
    principal_id = jwt_verify(check_auth_and_get_token(auth_token), method_arn)
    policy = generate_policy(principal_id, method_arn)
    return policy
