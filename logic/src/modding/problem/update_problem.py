from typing import Any, Dict
from modding.common import exception, settings, logging, http
from modding.problem import repository, models
from modding.utils import function
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    problem_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

PROBLEM_REPOSITORY = repository.ProblemRepository(_SETTINGS.problem_table_name)


class ProblemNotBuilt(exception.LoggingErrorException):
    def __init__(self, id: str, message: str):
        super().__init__("Problem could not be built %s, %s" % (id, message))


@function.decorator_builder(
    aws_client.ApiGateway.include_repos_action, PROBLEM_REPOSITORY
)
@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]) -> Any:
    try:
        updated_problem = update_problem(**event.body)

        response = http.get_response(
            http.HttpCodes.SUCCESS,
            body=updated_problem.dict(),
        )

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def build_updated_problem(problem_id: str, **kwargs) -> models.Problem:
    try:
        problem: models.Problem = PROBLEM_REPOSITORY.get_item_by_id(problem_id)
        problem_data = problem.dict()
        problem_data.update(**kwargs)
        problem_data.update({"id": problem_id})
        result = models.Problem(**problem_data)
    except Exception as e:
        raise ProblemNotBuilt(problem_id, e)

    return result


def update_problem(id: str, **kwargs) -> models.Problem:
    problem = build_updated_problem(id, **kwargs)
    PROBLEM_REPOSITORY.save_on_table(problem, update=True)
    return problem
