import json
import uuid
from typing import Any, Dict, Optional, Tuple
from modding.common import logging, settings, exception, http
from modding.video import repository, models


class _Settings(settings.Settings):
    video_bucket_name: str
    video_table_name: str
    upload_expire_time: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()


MAX_NUMBER_TRIES = 3

_VIDEO_REPOSITORY = repository.VideoRepository(
    _SETTINGS.video_table_name, _SETTINGS.video_bucket_name
)


class NoVideoNameException(exception.LoggingException):
    def __init__(self):
        super().__init__("There was no video name provided")


def handler(event: Dict[str, Any], context: Any) -> None:
    try:
        body = parse_body(event)

        video_created = create_video(**body)

        response = http.get_response(http.HttpCodes.SUCCESS, video_created)
    except:
        response = http.get_standard_error_response()
    return response


def parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = event.get("body") or str()
    return json.loads(body)


def generate_video_id(video_name: str):
    random_code = uuid.uuid4()
    return f"{video_name}-{random_code}"


def build_video_and_upload_url(video_name: str) -> Optional[Tuple[models.Video, str]]:
    video, upload_url = None, None
    tries = 0
    while tries < MAX_NUMBER_TRIES:
        try:
            video = models.Video(id=generate_video_id(video_name), name=video_name)
            upload_url = _VIDEO_REPOSITORY.get_video_bucket_presigned_url(
                video.id, int(_SETTINGS.upload_expire_time)
            )
            tries = MAX_NUMBER_TRIES
        except:
            tries += 1
            _LOGGER.warning(f"Video upload url could not be generated, try #{tries}")

    return video, upload_url


def create_video(video_name: str, **kwargs) -> Dict[str, Any]:
    result = {}
    if len(video_name):
        try:
            video, upload_url = build_video_and_upload_url(video_name)
            if video is not None and upload_url is not None:
                _VIDEO_REPOSITORY.save_video_data(video.dict())
            result = {**video.dict(), "upload_url": upload_url}
        except Exception as e:
            _LOGGER.error("Video has no been created, %s" % (e))
    else:
        raise NoVideoNameException()

    return result
