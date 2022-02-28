from typing import Any, Dict

from modding.problem.evaluation import repository
from modding.problem import models, repository as problem_repository
from modding.utils import id_generator, function
from modding.common import settings, logging, http, exception
from modding.common.aws_cli import AwsCustomClient as aws_client
from modding.utils import analizer


class _Settings(settings.Settings):
    problem_table_name: str
    problem_bucket_name: str
    problem_evaluation_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

BUILD_EVALUATION_MAX_TRIES = 1


PROBLEM_REPOSITORY = problem_repository.ProblemRepository(
    table_name=_SETTINGS.problem_table_name, bucket_name=_SETTINGS.problem_bucket_name
)

PROBLEM_EVALUATION_REPOSITORY = repository.ProblemEvaluationRepository(
    table_name=_SETTINGS.problem_evaluation_table_name
)


EVALUATION_ID_LENGTH = 10


CACHED_INPUTS = {}
CACHED_OUTPUTS = {}


class EvaluationFailedError(exception.LoggingException):
    def __init__(self, message: str):
        super().__init__("Could not analize %s" % (message))


@function.decorator_builder(
    aws_client.ApiGateway.include_repos_action, PROBLEM_EVALUATION_REPOSITORY
)
@aws_client.ApiGateway.pre_handler
def handler(event: aws_client.ApiGateway.AGWEvent, context: Dict[str, Any]) -> Any:
    try:
        evaluated = evaluate_problem(**event.body)

        response = http.get_response(
            http.HttpCodes.SUCCESS, body=evaluated.dict(exclude_none=True)
        )

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def _get_problem_test_case_upload_urls(problem: models.Problem) -> Dict[str, Any]:
    for i in range(len(problem.test_case)):
        file = problem.test_case[i]

        input_content = (
            CACHED_INPUTS.get(file.input_id)
            if file.input_id in CACHED_INPUTS
            else PROBLEM_REPOSITORY.get_file_content(file.input_id)
        )
        output_content = (
            CACHED_OUTPUTS.get(file.output_id)
            if file.output_id in CACHED_OUTPUTS
            else PROBLEM_REPOSITORY.get_file_content(file.output_id)
        )
        CACHED_INPUTS[file.input_id] = input_content
        CACHED_OUTPUTS[file.output_id] = output_content

        problem.test_case[i].input_data = input_content
        problem.test_case[i].output_data = output_content


def send_input_to_analyze(
    file_input: str,
    file_type: str,
    evaluation: models.ProblemEvaluation,
    problem: models.Problem,
) -> models.ProblemEvaluation:

    _get_problem_test_case_upload_urls(problem)

    analizer.Analizer().analyze(
        evaluation=evaluation,
        file_input=file_input,
        file_type=file_type,
        files=problem.test_case,
    )
    return evaluation


def evaluate(
    evaluation_data: Dict[str, Any],
    id: str,
    file_input: str,
    file_type: str,
    problem: models.Problem,
) -> models.ProblemEvaluation:
    evaluation_data.update({"id": id, "veredict": models.ProblemVeredict.SENT})
    evaluation = models.ProblemEvaluation.parse_obj(evaluation_data)
    PROBLEM_EVALUATION_REPOSITORY.save_on_table(evaluation)
    try:
        return send_input_to_analyze(file_input, file_type, evaluation, problem)
    except Exception as e:
        raise EvaluationFailedError(e)


def build_evaluation(
    problem_id: str, file_input: str, file_type: str
) -> models.ProblemEvaluation:
    problem = PROBLEM_REPOSITORY.get_item_by_id(problem_id)
    evaluation_data = {"problem_id": problem.id}
    result = id_generator.retrier_with_generator(
        problem.id,
        EVALUATION_ID_LENGTH,
        func=evaluate,
        params=(
            [],
            {
                "evaluation_data": evaluation_data,
                "file_input": file_input,
                "file_type": file_type,
                "problem": problem,
            },
        ),
        tries=BUILD_EVALUATION_MAX_TRIES,
        logging_method=_LOGGER.warning,
        failed_message="Could not evaluate problem",
    )
    return result


def evaluate_problem(**kwargs: Any) -> models.ProblemEvaluation:
    evaluation = build_evaluation(**kwargs)
    PROBLEM_EVALUATION_REPOSITORY.save_on_table(evaluation)
    return evaluation
