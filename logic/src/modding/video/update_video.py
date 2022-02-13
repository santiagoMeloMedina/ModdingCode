from typing import Any, Dict
from modding.common import exception, settings, logging, http
from modding.video import repository, models
from modding.utils import function
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    video_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

VIDEO_REPOSITORY = repository.VideoRepository(_SETTINGS.video_table_name)


class VideoNotBuilt(exception.LoggingErrorException):
    def __init__(self, id: str, message: str):
        super().__init__("Video could not be built %s, %s" % (id, message))


@function.decorator_builder(
    aws_client.ApiGateway.include_repos_action, VIDEO_REPOSITORY
)
@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]) -> Any:
    try:
        updated_video = update_video(**event.body)

        response = http.get_response(
            http.HttpCodes.SUCCESS,
            body=updated_video.dict(),
        )

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def build_updated_video(video_id: str, **kwargs) -> models.Video:
    try:
        video: models.Video = VIDEO_REPOSITORY.get_item_by_id(video_id)
        video_data = video.dict()
        video_data.update(**kwargs)
        video_data.update({"id": video_id})
        result = models.Video(**video_data)
    except Exception as e:
        raise VideoNotBuilt(video_id, e)

    return result


def update_video(id: str, **kwargs) -> models.Video:
    video = build_updated_video(id, **kwargs)
    VIDEO_REPOSITORY.save_on_table(video, update=True)
    return video
