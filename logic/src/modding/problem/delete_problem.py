from typing import Any, Dict
from modding.common import settings, logging, http
from modding.problem import repository
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    problem_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

PROBLEM_REPOSITORY = repository.ProblemRepository(_SETTINGS.problem_table_name)


@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]) -> Any:
    try:
        delete_problem(**event.body)

        response = http.get_standard_success_response()

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def delete_problem(id: str, **kwargs) -> None:
    PROBLEM_REPOSITORY.delete_data(id)
