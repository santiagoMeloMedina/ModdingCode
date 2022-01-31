from distutils.command.upload import upload
import json
import uuid
from typing import Any, Dict, Tuple
from modding.common import exception, settings, logging, http
from modding.minicourse import repository, models


class _Settings(settings.Settings):
    minicourse_bucket_name: str
    minicourse_table_name: str
    category_table_name: str
    thumb_upload_expire_time: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

MINICOURSE_REPOSITORY = repository.MinicourseRepository(
    _SETTINGS.minicourse_table_name,
    _SETTINGS.minicourse_bucket_name,
    _SETTINGS.category_table_name,
)

MAX_NUMBER_TRIES = 3


class MinicourseNotBuilt(exception.LoggingErrorException):
    def __init__(self):
        super().__init__("Minicourse could not be built")


def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Any:
    try:
        body = parse_body(event)

        created_minicourse, thumb_upload_url = create_minicourse(**body)

        response = http.get_response(
            http.HttpCodes.SUCCESS,
            body={**created_minicourse.dict(), "thumb_upload_url": thumb_upload_url},
        )

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def parse_body(event: Dict[str, Any]) -> Dict[str, Any]:
    body = event.get("body") or str()
    return json.loads(body)


def generate_id(category_id: str) -> str:
    random_code = uuid.uuid4()
    return f"{category_id}-{random_code}"


def clean_extension(extension: str) -> str:
    result = []
    for character in extension:
        if character.isalpha():
            result.append(character)

    return "".join(result)


def build_minicourse(
    name: str, category_id: str, thumb_ext: str
) -> Tuple[models.Minicourse, str]:
    minicourse, thumb_upload_url = None, None
    tries = 0
    while tries < MAX_NUMBER_TRIES:
        try:
            minicourse = models.Minicourse(
                id=generate_id(category_id), name=name, category_id=category_id
            )
            thumb_upload_url = MINICOURSE_REPOSITORY.get_thumb_put_presigned_url(
                f"{minicourse.id}.{clean_extension(thumb_ext)}",
                int(_SETTINGS.thumb_upload_expire_time),
            )
            tries = MAX_NUMBER_TRIES
        except:
            tries += 1
            _LOGGER.warning(f"Thumb upload url could not be generated, try #{tries}")

    return minicourse, thumb_upload_url


def create_minicourse(
    name: str, category_id: str, thumb_ext: str, **kwargs
) -> Tuple[models.Minicourse, str]:
    category = MINICOURSE_REPOSITORY.get_category_by_id(category_id)
    minicourse, thumb_upload_url = build_minicourse(name, category.id, thumb_ext)
    if minicourse is not None and thumb_upload_url is not None:
        MINICOURSE_REPOSITORY.save_data(minicourse)
    else:
        raise MinicourseNotBuilt()

    return minicourse, thumb_upload_url
