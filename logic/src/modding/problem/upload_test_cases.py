from typing import Any, Dict
from modding.common import exception, settings, logging, http
from modding.problem import repository, models
from modding.utils import function
from modding.common.aws_cli import AwsCustomClient as aws_client


class _Settings(settings.Settings):
    problem_table_name: str
    problem_bucket_name: str
    upload_url_expire_time: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

PROBLEM_REPOSITORY = repository.ProblemRepository(
    _SETTINGS.problem_table_name, _SETTINGS.problem_bucket_name
)


class ProblemNotBuilt(exception.LoggingErrorException):
    def __init__(self, id: str, message: str):
        super().__init__("Problem could not be built %s, %s" % (id, message))


@function.decorator_builder(
    aws_client.ApiGateway.include_repos_action, PROBLEM_REPOSITORY
)
@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]) -> Any:
    try:
        problem_and_generated_urls = update_problem_and_generate_urls(**event.body)

        response = http.get_response(
            http.HttpCodes.SUCCESS,
            body=problem_and_generated_urls,
        )

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def build_updated_problem(
    problem_id: str, input_name: str, output_name: str, **kwargs
) -> models.Problem:
    try:
        problem: models.Problem = PROBLEM_REPOSITORY.get_item_by_id(problem_id)
        common_id = lambda _name: f"{problem.id}-{len(problem.test_case or [])}_{_name}"
        common_file_id = lambda _type: f"{common_id(_type)}.txt"
        problem_data = problem.dict()
        problem_data.update({"id": problem_id})
        new_test_case = models.ProblemInputFile(
            id=common_id("test"),
            input_name=input_name,
            output_name=output_name,
            input_id=common_file_id("input"),
            output_id=common_file_id("output"),
        )
        result = models.Problem(
            **problem_data, test_case=problem.test_case + [new_test_case]
        )
    except Exception as e:
        raise ProblemNotBuilt(problem_id, e)

    return result


def get_problem_test_case_upload_urls(problem: models.Problem) -> Dict[str, Any]:
    input_upload_url = PROBLEM_REPOSITORY.file_put_presigned_url(
        problem.test_case[-1].input_id, int(_SETTINGS.upload_url_expire_time)
    )
    output_upload_url = PROBLEM_REPOSITORY.file_put_presigned_url(
        problem.test_case[-1].output_id, int(_SETTINGS.upload_url_expire_time)
    )
    return {"input_url": input_upload_url, "output_url": output_upload_url}


def update_problem_and_generate_urls(id: str, **kwargs) -> Dict[str, Any]:
    problem = build_updated_problem(id, **kwargs)
    PROBLEM_REPOSITORY.save_on_table(problem, update=True)
    upload_urls = get_problem_test_case_upload_urls(problem)
    return {**problem.dict(), **upload_urls}
