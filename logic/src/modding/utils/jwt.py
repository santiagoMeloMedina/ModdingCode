from typing import Any, Dict
import jwt
from modding.common import exception


class AuthorizationHeaderValueError(exception.LoggingErrorException):
    def __init__(self):
        super().__init__("Authorization headers has an incorrect format")


class TokenDecodeError(exception.LoggingErrorException):
    def __init__(self, e: Any):
        super().__init__("There was an error decoding jwt token, %s" % (e))


def decode_hs256_token_no_verify(token: str) -> Dict[str, Any]:
    try:
        payload = jwt.decode(
            token, algorithms="HS256", options={"verify_signature": False}
        )
        return payload
    except Exception as e:
        raise TokenDecodeError(e)


def obtain_token_from_bearer(value: str) -> str:
    data = value.split(" ")
    if len(data) == 2:
        return data[1]
    else:
        raise AuthorizationHeaderValueError()
