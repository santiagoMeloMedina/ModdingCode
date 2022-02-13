from typing import Any, Dict
from modding.common import exception, settings, logging, http
from modding.minicourse.category import repository
from modding.minicourse import models
from modding.utils import function
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    category_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

CATEGORY_REPOSITORY = repository.CategoryRepository(_SETTINGS.category_table_name)


class CategoryNotBuilt(exception.LoggingErrorException):
    def __init__(self, id: str, message: str):
        super().__init__("Category could not be built %s, %s" % (id, message))


@function.decorator_builder(
    aws_client.ApiGateway.include_repos_action, CATEGORY_REPOSITORY
)
@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]) -> Any:
    try:
        updated_category = update_category(**event.body)

        response = http.get_response(
            http.HttpCodes.SUCCESS,
            body=updated_category.dict(),
        )

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def build_updated_category(category_id: str, **kwargs) -> models.Category:
    try:
        category: models.Category = CATEGORY_REPOSITORY.get_item_by_id(category_id)
        category_data = category.dict()
        category_data.update(**kwargs)
        category_data.update({"id": category_id})
        result = models.Category(**category_data)
    except Exception as e:
        raise CategoryNotBuilt(category_id, e)

    return result


def update_category(id: str, **kwargs) -> models.Category:
    category = build_updated_category(id, **kwargs)
    CATEGORY_REPOSITORY.save_on_table(category, update=True)
    return category
