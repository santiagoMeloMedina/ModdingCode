from typing import Any, Dict, List
from modding.common import http, logging, settings, exception
from modding.minicourse import repository, models
from modding.utils import files


class _Settings(settings.Settings):
    minicourse_table_name: str
    minicourse_bucket_name: str
    thumb_download_expire_time: str
    thumb_upload_expire_time: str
    multiple_minicourse_retrival_limit: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()


MINICOURSE_REPOSITORY = repository.MinicourseRepository(
    table_name=_SETTINGS.minicourse_table_name,
    bucket_name=_SETTINGS.minicourse_bucket_name,
)


class TooManyMinicoursesRetrival(exception.LoggingErrorException):
    def __init__(self):
        super().__init__("Too many minicourses to retrieve at once")


def handler(event: Dict[str, Any], context: Dict[str, Any]):
    try:
        body = http.parse_body(event)
        result = actions(**body)

        response = http.get_response(http.HttpCodes.SUCCESS, body=result)
    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()
    return response


def get_minicourse(id: str, get_thumb: bool = False, **kwargs) -> Dict[str, Any]:
    minicourse: models.Minicourse = MINICOURSE_REPOSITORY.get_item_by_id(id)
    object_name = f"{id}.{files.clean_extension(minicourse.thumb_ext)}"
    if get_thumb:
        thumb_download_url = MINICOURSE_REPOSITORY.thumb_get_presigned_url(
            object_name, int(_SETTINGS.thumb_download_expire_time)
        )
        result = {
            "minicourse": minicourse.dict(),
            "thumb_download_url": thumb_download_url,
        }
    else:
        result = {"minicourse": minicourse.dict()}

    return result


def get_multiple_minicourses(
    ids: List[str], get_thumb: bool = False, **kwargs
) -> Dict[str, Any]:
    if len(ids) <= int(_SETTINGS.multiple_minicourse_retrival_limit):
        result = []
        for id in ids:
            result.append(get_minicourse(id, get_thumb))
        return {"minicourses": result}
    else:
        raise TooManyMinicoursesRetrival()


def get_minicourse_thumb_upload_url(id: str, **kwargs) -> Dict[str, Any]:
    minicourse: models.Minicourse = MINICOURSE_REPOSITORY.get_item_by_id(id)
    object_name = f"{id}.{files.clean_extension(minicourse.thumb_ext)}"
    thumb_upload_url = MINICOURSE_REPOSITORY.thumb_put_presigned_url(
        object_name, int(_SETTINGS.thumb_upload_expire_time)
    )
    return {"thumb_upload_url": thumb_upload_url}


def actions(action: str, params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    mapped_actions = {
        "get_minicourse": get_minicourse,
        "get_multiple_minicourses": get_multiple_minicourses,
        "get_minicourse_thumb_upload_url": get_minicourse_thumb_upload_url,
    }

    def empty(**kwargs):
        _LOGGER.error("No registered action given")

    return (mapped_actions.get(action) or empty)(**params)
