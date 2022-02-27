from typing import Any, Dict, Tuple
from modding.common import exception, settings, logging, http
from modding.minicourse import repository, models
from modding.utils import id_generator, files, function
from modding.minicourse.category import repository as category_repository
from modding.common.aws_cli import AwsCustomClient as aws_client


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


@function.decorator_builder(
    aws_client.ApiGateway.include_repos_action, MINICOURSE_REPOSITORY
)
@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]) -> Any:
    try:
        created_minicourse, thumb_upload_url = create_minicourse(**event.body)

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
) -> models.Minicourse:
    ext = files.clean_extension(ext)
    minicourse = models.Minicourse(id=id, name=name, category_id=category_id, ext=ext)
    return minicourse


def build_minicourse(name: str, category_id: str, ext: str) -> models.Minicourse:
    return id_generator.retrier_with_generator(
        category_id,
        MINICOURSE_ID_LENGTH,
        func=build_and_get_upload_url,
        params=([], {"name": name, "ext": ext, "category_id": category_id}),
        tries=MAX_NUMBER_TRIES,
        logging_method=_LOGGER.warning,
        failed_message="Minicourse could not be built",
    )


def obtain_upload_url(minicourse: models.Minicourse) -> str:
    thumb_upload_url = MINICOURSE_REPOSITORY.thumb_put_presigned_url(
        f"{minicourse.id}.{minicourse.ext}",
        int(_SETTINGS.thumb_upload_expire_time),
    )
    return thumb_upload_url


def create_minicourse(
    name: str, category_id: str, ext: str, **kwargs
) -> Tuple[models.Minicourse, str]:
    category: models.Category = CATEGORY_REPOSITORY.get_item_by_id(category_id)
    minicourse = build_minicourse(name, category.id, ext)
    if minicourse is not None:
        MINICOURSE_REPOSITORY.save_on_table(minicourse)
        thumb_upload_url = obtain_upload_url(minicourse)
    else:
        raise MinicourseNotBuilt()

    return minicourse, thumb_upload_url
