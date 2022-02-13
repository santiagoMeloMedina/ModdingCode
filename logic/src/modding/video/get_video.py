from typing import Any, Dict
from modding.common import http, logging, settings
from modding.video import repository, models
from modding.utils import function, files
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    video_table_name: str
    video_bucket_name: str
    video_minicourse_index_name: str
    video_download_expire_time: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()


VIDEO_REPOSITORY = repository.VideoRepository(
    table_name=_SETTINGS.video_table_name, bucket_name=_SETTINGS.video_bucket_name
)


@function.decorator_builder(
    aws_client.ApiGateway.include_repos_action, VIDEO_REPOSITORY
)
@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]):
    try:
        result = actions(**event.body)

        response = http.get_response(http.HttpCodes.SUCCESS, body=result)
    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()
    return response


def get_videos_by_minicourse(minicourse_id: str, **kwargs) -> Dict[str, Any]:
    videos = VIDEO_REPOSITORY.query_items(
        {"minicourse_id": minicourse_id},
        index_name=_SETTINGS.video_minicourse_index_name,
    )
    return {"videos": [video.dict() for video in videos]}


def _get_video_download_url(video: models.Video) -> str:
    object_name = f"{video.id}.{files.clean_extension(video.ext)}"
    return VIDEO_REPOSITORY.video_download_presigned_url(
        object_name, int(_SETTINGS.video_download_expire_time)
    )


def get_video_by_id(id: str, get_video_url: bool = False, **kwargs) -> Dict[str, Any]:
    video = VIDEO_REPOSITORY.get_item_by_id(id)
    return {
        **video.dict(),
        **(
            {"video_download_url": _get_video_download_url(video)}
            if get_video_url
            else {}
        ),
    }


def actions(action: str, params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    mapped_actions = {
        "get_videos_by_minicourse": get_videos_by_minicourse,
        "get_video_by_id": get_video_by_id,
    }

    def empty(**kwargs):
        _LOGGER.error("No registered action given")

    return (mapped_actions.get(action) or empty)(**params)
