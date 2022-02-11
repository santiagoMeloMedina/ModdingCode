from typing import Any, Dict

from modding.problem import models, repository
from modding.utils import id_generator
from modding.common import settings, logging, http
from modding.minicourse import repository as minicourse_repository


class _Settings(settings.Settings):
    problem_table_name: str
    problem_bucket_name: str
    minicourse_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

BUILD_PROBLEM_MAX_TRIES = 2


PROBLEM_REPOSITORY = repository.ProblemRepository(
    table_name=_SETTINGS.problem_table_name, bucket_name=_SETTINGS.problem_bucket_name
)

MINICOURSE_REPOSITORY = minicourse_repository.MinicourseRepository(
    table_name=_SETTINGS.minicourse_table_name
)


PROBLEM_ID_LENGTH = 10


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


def build(problem_data: Dict[str, Any], id: str) -> models.Problem:
    problem_data.update({"id": id, "status": models.ProblemStatus.CREATED})
    result = models.Problem.parse_obj(problem_data)
    return result


def build_problem(minicourse_id: str, name: str, difficulty: int) -> models.Problem:
    problem_data = {
        "minicourse_id": minicourse_id,
        "name": name,
        "difficulty": difficulty,
    }
    result = id_generator.retrier_with_generator(
        minicourse_id,
        PROBLEM_ID_LENGTH,
        func=build,
        params=(
            [],
            {"problem_data": problem_data},
        ),
        tries=BUILD_PROBLEM_MAX_TRIES,
        logging_method=_LOGGER.warning,
        failed_message="Could not build problem",
    )
    return result


def create_problem(**kwargs: Any) -> models.Problem:
    problem = build_problem(**kwargs)
    PROBLEM_REPOSITORY.save_on_table(problem)
    return problem
