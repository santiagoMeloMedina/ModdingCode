import enum
from typing import Any, Dict, Union


class HttpCodes(enum.Enum):
    SUCCESS = 200
    ACCEPTED = 300
    ERROR = 500
    BAD_REQUEST = 400


def get_response(code: HttpCodes, body: Union[Dict[str, Any], str]) -> Dict[str, Any]:
    return {"statusCode": code.value, "body": body}


def get_standard_error_response() -> Dict[str, Any]:
    return get_response(HttpCodes.ERROR, "Error")
