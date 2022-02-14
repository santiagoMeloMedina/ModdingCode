from typing import Any, Dict, List
from modding.common import http, logging, settings
from modding.problem.evaluation import repository
from modding.utils import function
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    problem_evaluation_table_name: str
    evaluation_problem_index_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()


PROBLEM_EVALUATION_REPOSITORY = repository.ProblemEvaluationRepository(
    table_name=_SETTINGS.problem_evaluation_table_name
)


@function.decorator_builder(
    aws_client.ApiGateway.include_repos_action, PROBLEM_EVALUATION_REPOSITORY
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


def get_evaluations_by_username(problem_id: str, **kwargs) -> Dict[str, Any]:
    evaluations = PROBLEM_EVALUATION_REPOSITORY.query_items_by_username(
        {"problem_id": problem_id}, index_name=_SETTINGS.evaluation_problem_index_name
    )
    return {"evaluations": [evaluation.dict() for evaluation in evaluations]}


def actions(action: str, params: Dict[str, Any], **kwargs) -> Dict[str, Any]:
    mapped_actions = {"get_evaluations_by_username": get_evaluations_by_username}

    def empty(**kwargs):
        _LOGGER.error("No registered action given")

    return (mapped_actions.get(action) or empty)(**params)
