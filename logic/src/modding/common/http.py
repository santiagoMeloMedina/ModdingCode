import enum
import json
from typing import Any, Dict, Union


class HttpCodes(enum.Enum):
    SUCCESS = 200
    ACCEPTED = 300
    ERROR = 500
    BAD_REQUEST = 400


def get_response(code: HttpCodes, body: Union[Dict[str, Any], str]) -> Dict[str, Any]:
    return {"statusCode": code.value, "body": json.dumps(body)}


def get_standard_success_response() -> Dict[str, Any]:
    return get_response(HttpCodes.SUCCESS, "Success")


def get_standard_error_response() -> Dict[str, Any]:
    return get_response(HttpCodes.ERROR, "Error")


def parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = event.get("body") or str()
    return json.loads(body)
