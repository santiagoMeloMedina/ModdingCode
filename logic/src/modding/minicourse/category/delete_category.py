from typing import Any, Dict
from modding.common import settings, logging, http
from modding.minicourse.category import repository
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    category_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

CATEGORY_REPOSITORY = repository.CategoryRepository(_SETTINGS.category_table_name)


@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]) -> Any:
    try:
        delete_category(**event.body)

        response = http.get_standard_success_response()

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def delete_category(id: str, **kwargs) -> None:
    CATEGORY_REPOSITORY.delete_data(id)
