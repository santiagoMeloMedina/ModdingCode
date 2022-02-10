from typing import Any, Dict
from modding.common import exception, settings, logging, http
from modding.minicourse import repository, models


class _Settings(settings.Settings):
    minicourse_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

MINICOURSE_REPOSITORY = repository.MinicourseRepository(_SETTINGS.minicourse_table_name)


class MinicourseNotBuilt(exception.LoggingErrorException):
    def __init__(self, id: str, message: str):
        super().__init__("Minicourse could not be built %s, %s" % (id, message))


def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Any:
    try:
        body = http.parse_body(event)

        updated_minicourse = update_minicourse(**body)

        response = http.get_response(
            http.HttpCodes.SUCCESS,
            body=updated_minicourse.dict(),
        )

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def build_updated_minicourse(minicourse_id: str, **kwargs) -> models.Minicourse:
    try:
        minicourse: models.Minicourse = MINICOURSE_REPOSITORY.get_item_by_id(
            minicourse_id
        )
        minicourse_data = minicourse.dict()
        minicourse_data.update(**kwargs)
        minicourse_data.update({"id": minicourse_id})
        result = models.Minicourse(**minicourse_data)
    except Exception as e:
        raise MinicourseNotBuilt(minicourse_id, e)

    return result


def update_minicourse(id: str, **kwargs) -> models.Minicourse:
    minicourse = build_updated_minicourse(id, **kwargs)
    MINICOURSE_REPOSITORY.save_on_table(minicourse, update=True)
    return minicourse
