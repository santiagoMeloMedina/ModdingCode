from typing import Any, Dict, Tuple
from modding.common import exception, settings, logging, http
from modding.minicourse import repository, models
from modding.utils import id_generator, files
from modding.minicourse.category import repository as category_repository


class _Settings(settings.Settings):
    minicourse_bucket_name: str
    minicourse_table_name: str
    category_table_name: str
    thumb_upload_expire_time: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

MINICOURSE_REPOSITORY = repository.MinicourseRepository(
    _SETTINGS.minicourse_table_name, _SETTINGS.minicourse_bucket_name
)

CATEGORY_REPOSITORY = category_repository.CategoryRepository(
    _SETTINGS.category_table_name
)

MAX_NUMBER_TRIES = 3
MINICOURSE_ID_LENGTH = 8


class MinicourseNotBuilt(exception.LoggingErrorException):
    def __init__(self):
        super().__init__("Minicourse could not be built")


def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Any:
    try:
        body = http.parse_body(event)

        created_minicourse, thumb_upload_url = create_minicourse(**body)

        response = http.get_response(
            http.HttpCodes.SUCCESS,
            body={**created_minicourse.dict(), "thumb_upload_url": thumb_upload_url},
        )

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def build_and_get_upload_url(
    name: str, ext: str, category_id: str, id: str
) -> Tuple[models.Minicourse, str]:
    ext = files.clean_extension(ext)
    minicourse = models.Minicourse(id=id, name=name, category_id=category_id, ext=ext)
    thumb_upload_url = MINICOURSE_REPOSITORY.thumb_put_presigned_url(
        f"{minicourse.id}.{ext}",
        int(_SETTINGS.thumb_upload_expire_time),
    )

    return minicourse, thumb_upload_url


def build_minicourse(
    name: str, category_id: str, ext: str
) -> Tuple[models.Minicourse, str]:
    return id_generator.retrier_with_generator(
        category_id,
        MINICOURSE_ID_LENGTH,
        func=build_and_get_upload_url,
        params=([], {"name": name, "ext": ext, "category_id": category_id}),
        tries=MAX_NUMBER_TRIES,
        logging_method=_LOGGER.warning,
        failed_message="Thumb upload url could not be generated",
    )


def create_minicourse(
    name: str, category_id: str, ext: str, **kwargs
) -> Tuple[models.Minicourse, str]:
    category: models.Category = CATEGORY_REPOSITORY.get_item_by_id(category_id)
    minicourse, thumb_upload_url = build_minicourse(name, category.id, ext)
    if minicourse is not None and thumb_upload_url is not None:
        MINICOURSE_REPOSITORY.save_on_table(minicourse)
    else:
        raise MinicourseNotBuilt()

    return minicourse, thumb_upload_url
