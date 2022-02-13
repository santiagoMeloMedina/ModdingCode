from typing import Any, Dict, Tuple
from modding.common import logging, settings, http
from modding.video import repository, models
from modding.utils import id_generator, files, function
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    video_bucket_name: str
    video_table_name: str
    upload_expire_time: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()


MAX_NUMBER_TRIES = 3

VIDEO_ID_LENGTH = 8

_VIDEO_REPOSITORY = repository.VideoRepository(
    _SETTINGS.video_table_name, _SETTINGS.video_bucket_name
)


@function.decorator_builder(
    aws_client.ApiGateway.include_repos_action, _VIDEO_REPOSITORY
)
@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Any) -> None:
    try:
        video_created = create_video(**event.body)

        response = http.get_response(http.HttpCodes.SUCCESS, video_created)
    except Exception as e:
        response = http.get_standard_error_response()
        _LOGGER.error(e)
    return response


def build(
    minicourse_id: str, name: str, id: str, ext: str, section: str
) -> Tuple[models.Video, str]:
    video_ext = files.clean_extension(ext)
    video = models.Video(
        id=id,
        name=name,
        ext=video_ext,
        minicourse_id=minicourse_id,
        section=models.VideoSections(section),
    )
    upload_url = _VIDEO_REPOSITORY.video_presigned_url(
        f"{video.id}.{video_ext}", int(_SETTINGS.upload_expire_time)
    )
    return video, upload_url


def build_video_and_upload_url(
    minicourse_id: str, name: str, ext: str, section: str
) -> Tuple[models.Video, str]:
    return id_generator.retrier_with_generator(
        minicourse_id,
        VIDEO_ID_LENGTH,
        func=build,
        params=(
            [],
            {
                "name": name,
                "minicourse_id": minicourse_id,
                "ext": ext,
                "section": section,
            },
        ),
        tries=MAX_NUMBER_TRIES,
        logging_method=_LOGGER.warning,
        failed_message="Video upload url could not be generated",
    )


def create_video(**kwargs) -> Dict[str, Any]:
    video, upload_url = build_video_and_upload_url(**kwargs)
    _VIDEO_REPOSITORY.save_on_table(video)
    result = {"video": video.dict(), "upload_url": upload_url}
    return result
