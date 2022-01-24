import json
from typing import Any, Dict
from modding.common import logging, aws_cli, settings, exception, http


class _Settings(settings.Settings):
    video_bucket_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()


class NoVideoNameException(exception.LoggingException):
    def __init__(self):
        super().__init__("There was no video name provided")


class S3PresigningError(exception.LoggingErrorException):
    def __init__(self, message: str):
        super().__init__("Can not get presigned url, %s" % (message))


def handler(event: Dict[str, Any], context: Any) -> None:
    try:
        body = parse_body(event)
        presigned_url = get_put_presigned_url(
            video_name=body.get("video_name") or str()
        )

        response = http.get_response(
            http.HttpCodes.SUCCESS, {"presigned_put_url": presigned_url}
        )
    except:
        response = http.get_standard_error_response()
    return response


def parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = event.get("body") or str()
    return json.loads(body)


def get_put_presigned_url(video_name: str) -> str:
    if len(video_name):
        try:
            s3 = aws_cli.AwsCustomClient.s3()
            put_url = s3.put_presigned_url(
                bucket_name=_SETTINGS.video_bucket_name,
                object_name=video_name,
            )
        except Exception as e:
            raise S3PresigningError(e)
    else:
        raise NoVideoNameException()
    return put_url
