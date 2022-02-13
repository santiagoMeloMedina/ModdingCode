from typing import Any, Dict

from modding.problem.evaluation import repository
from modding.problem import models, repository as problem_repository
from modding.utils import id_generator
from modding.common import settings, logging, http, exception


class _Settings(settings.Settings):
    problem_table_name: str
    problem_evaluation_table_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()

BUILD_EVALUATION_MAX_TRIES = 3


PROBLEM_REPOSITORY = problem_repository.ProblemRepository(
    table_name=_SETTINGS.problem_table_name
)

PROBLEM_EVALUATION_REPOSITORY = repository.ProblemEvaluationRepository(
    table_name=_SETTINGS.problem_evaluation_table_name,
)


EVALUATION_ID_LENGTH = 10


class FileInputNotSentError(exception.LoggingException):
    def __init__(self):
        super().__init__("Could not send file input to analizer")


def handler(event: Dict[str, Any], context: Dict[str, Any]) -> Any:
    try:
        body = http.parse_body(event)

        evaluated = evaluate_problem(**body)

        response = http.get_response(http.HttpCodes.SUCCESS, body=evaluated.dict())

    except Exception as e:
        _LOGGER.error(e)
        response = http.get_standard_error_response()

    return response


def send_input_to_analyze(file_input: str) -> bool:
    ## TODO(Santiago): Implement the sending of this input file when analyzer is created
    return True


def evaluate(
    evaluation_data: Dict[str, Any], id: str, file_input: str
) -> models.ProblemEvaluation:
    evaluation_data.update({"id": id, "veredict": models.ProblemVeredict.SENT})
    if send_input_to_analyze(file_input):
        result = models.ProblemEvaluation.parse_obj(evaluation_data)
        return result
    else:
        raise FileInputNotSentError()


def build_evaluation(problem_id: str, file_input: str) -> models.ProblemEvaluation:
    problem = PROBLEM_REPOSITORY.get_item_by_id(problem_id)
    evaluation_data = {"problem_id": problem.id}
    result = id_generator.retrier_with_generator(
        problem.id,
        EVALUATION_ID_LENGTH,
        func=evaluate,
        params=(
            [],
            {"evaluation_data": evaluation_data, "file_input": file_input},
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
