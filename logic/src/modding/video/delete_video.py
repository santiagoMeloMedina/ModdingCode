from typing import Any, Dict
from modding.common import settings, logging, http
from modding.video import repository
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    video_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

VIDEO_REPOSITORY = repository.VideoRepository(_SETTINGS.video_table_name)


@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]) -> Any:
    try:
        delete_video(**event.body)

        response = http.get_standard_success_response()

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def delete_video(id: str, **kwargs) -> None:
    VIDEO_REPOSITORY.delete_data(id)
