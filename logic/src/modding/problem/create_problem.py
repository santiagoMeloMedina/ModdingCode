from typing import Any, Dict
from modding.problem import models, repository
from modding.utils import id_generator
from modding.common import settings, logging, http


class _Settings(settings.Settings):
    problem_table_name: str
    problem_bucket_name: str
    minicourse_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

BUILD_PROBLEM_MAX_TRIES = 2


PROBLEM_REPOSITORY = repository.ProblemRepository(
    _SETTINGS.problem_table_name,
    _SETTINGS.problem_bucket_name,
    _SETTINGS.minicourse_table_name,
)


def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Any:
    try:
        body = http.parse_body(event)

        created_problem = create_problem(**body)

        response = http.get_response(
            http.HttpCodes.SUCCESS, body=created_problem.dict()
        )

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def build(body: Dict[str, Any], id: str) -> models.Problem:
    body.update({"id": id, "status": models.ProblemStatus.CREATED})
    result = models.Problem.parse_obj(body)
    return result


def build_problem(body: Dict[str, Any]) -> models.Problem:
    result = None
    if "name" in body and "minicourse_id" in body:
        PROBLEM_REPOSITORY.get_minicourse_by_id(minicourse_id=body.get("minicourse_id"))
        result = id_generator.retrier_with_generator(
            body.get("name"),
            func=build,
            params=([], {"body": body}),
            tries=BUILD_PROBLEM_MAX_TRIES,
            logging_method=_LOGGER.warning,
            failed_message="Could not build problem",
        )
    return result


def create_problem(problem_body: Dict[str, Any], **kwargs: Any) -> models.Problem:
    problem = build_problem(body=problem_body)
    PROBLEM_REPOSITORY.save_on_table(problem)
    return problem
