from typing import Any, Dict

from modding.minicourse.category import repository
from modding.minicourse import models
from modding.utils import id_generator
from modding.common import settings, logging, http


class _Settings(settings.Settings):
    category_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

BUILD_CATEGORY_MAX_TRIES = 1
CATEGORY_ID_LENGTH = 10


CATEGORY_REPOSITORY = repository.CategoryRepository(
    table_name=_SETTINGS.category_table_name
)


def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Any:
    try:
        body = http.parse_body(event)

        created = create_category(**body)

        response = http.get_response(http.HttpCodes.SUCCESS, body=created.dict())

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def build(name: str, description: str, id: str) -> models.Category:
    category = models.Category(id=id, name=name, description=description)
    return category


def build_with_id(name: str, description: str) -> models.Category:
    result = id_generator.retrier_with_generator(
        "cat",
        CATEGORY_ID_LENGTH,
        func=build,
        params=(
            [],
            {"name": name, "description": description},
        ),
        tries=BUILD_CATEGORY_MAX_TRIES,
        logging_method=_LOGGER.warning,
        failed_message="Could not create category",
    )
    return result


def create_category(**kwargs: Any) -> models.Category:
    category = build_with_id(**kwargs)
    CATEGORY_REPOSITORY.save_on_table(category)
    return category
