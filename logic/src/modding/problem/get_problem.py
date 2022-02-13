from typing import Any, Dict
from modding.common import http, logging, settings
from modding.problem import repository
from modding.utils import function
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    problem_table_name: str
    problem_minicourse_index_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()


PROBLEM_REPOSITORY = repository.ProblemRepository(
    table_name=_SETTINGS.problem_table_name,
)


@function.decorator_builder(
    aws_client.ApiGateway.include_repos_action, PROBLEM_REPOSITORY
)
@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]):
    try:
        result = actions(**event.body)

        response = http.get_response(http.HttpCodes.SUCCESS, body=result)
    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()
    return response


def get_problems_by_minicourse(minicourse_id: str, **kwargs) -> Dict[str, Any]:
    problems = PROBLEM_REPOSITORY.query_items(
        {"minicourse_id": minicourse_id},
        index_name=_SETTINGS.problem_minicourse_index_name,
    )
    return {"problems": [problem.dict() for problem in problems]}


def get_problem_by_id(id: str, **kwargs) -> Dict[str, Any]:
    problem = PROBLEM_REPOSITORY.get_item_by_id(id)
    return problem.dict()


def actions(action: str, params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    mapped_actions = {
        "get_problems_by_minicourse": get_problems_by_minicourse,
        "get_problem_by_id": get_problem_by_id,
    }

    def empty(**kwargs):
        _LOGGER.error("No registered action given")

    return (mapped_actions.get(action) or empty)(**params)
