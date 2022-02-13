from typing import Any, Dict
from modding.common import http, logging, settings
from modding.minicourse.category import repository
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    category_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()


CATEGORY_REPOSITORY = repository.CategoryRepository(
    table_name=_SETTINGS.category_table_name,
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


def get_all_categories(**kwargs) -> Dict[str, Any]:
    categories = CATEGORY_REPOSITORY.scan_items({})
    return {"categories": [category.dict() for category in categories]}


def actions(action: str, params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    mapped_actions = {"get_all_categories": get_all_categories}

    def empty(**kwargs):
        _LOGGER.error("No registered action given")

    return (mapped_actions.get(action) or empty)(**params)
