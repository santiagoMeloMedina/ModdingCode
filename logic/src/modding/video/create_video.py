import json
import uuid
from typing import Any, Dict, Optional
from modding.common import logging, aws_cli, settings, exception, http
from modding.video.utils import date_format


class _Settings(settings.Settings):
    video_bucket_name: str
    video_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()


MAX_NUMBER_TRIES = 3


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

def generate_video_id(video_name: str):
    random_code_pre = uuid.uuid4()
    random_code_sub = uuid.uuid4()
    return f"{random_code_pre}-{video_name}-{random_code_sub}"

def get_put_presigned_url(video_id: str) -> str:
    try:
        s3 = aws_cli.AwsCustomClient.s3()
        put_url = s3.put_presigned_url(
            bucket_name=_SETTINGS.video_bucket_name,
            object_name=video_id,
        )
    except Exception as e:
        raise S3PresigningError(e)
    return put_url


def generate_upload_url(video_name: str) -> Optional[str]:
    upload_url = None
    tries = 0
    while tries < MAX_NUMBER_TRIES:
        try:
            video_id = generate_video_id(video_name)
            upload_url = get_put_presigned_url(video_id)
            tries = MAX_NUMBER_TRIES
        except:
            tries += 1
            _LOGGER.warning(f"Video upload url could not be generated, try #{tries}")
    
    return upload_url

def build_video(video_name: str) -> Dict[str, Any]:
    date = date_format.get_now_unix_time()
    return {
        "date": date,
        "name": video_name
    }

def create_video(video_name: str) -> str:
    if len(video_name):
        try:
            dynamodb = aws_cli.AwsCustomClient.dynamo(
                table_name=_SETTINGS.video_table_name
            )

            built_video_item = build_video(video_name)
            dynamodb.put_item(built_video_item)

            upload_url = generate_upload_url(video_name)
        except:
            print("f")
    else:
        raise NoVideoNameException()