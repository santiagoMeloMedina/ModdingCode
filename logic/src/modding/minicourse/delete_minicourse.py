from typing import Any, Dict
from modding.common import settings, logging, http
from modding.minicourse import repository
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    minicourse_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

MINICOURSE_REPOSITORY = repository.MinicourseRepository(_SETTINGS.minicourse_table_name)


@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]) -> Any:
    try:
        delete_minicourse(**event.body)

        response = http.get_standard_success_response()

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def delete_minicourse(id: str, **kwargs) -> None:
    MINICOURSE_REPOSITORY.delete_data(id)
