import os
from typing import Any
from unittest.mock import Mock, patch
import pytest
import copy


class AnyStr(str):
    def __eq__(self, other: Any):
        return True


_DEFAULT_ENVIRONMENT = {
    "PROBLEM_TABLE_NAME": "",
    "PROBLEM_BUCKET_NAME": "",
    "PROBLEM_EVALUATION_TABLE_NAME": "",
    "PROBLEM_EVALUATION_BUCKET_NAME": "",
}

MOCK_PROBLEM_EVALUATION_ID = "prefix-12341"
MOCK_PROBLEM_EVALUATION = {"problem_id": "problem1", "username": "user1@gmail.com"}

MOCK_PROBLEM = {
    "id": "min1-veevcf32",
    "name": "problem1",
    "minicourse_id": "min1",
    "difficulty": 1,
    "status": "CREATED",
}

MOCK_FILE_INPUT = ""


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
def test_evaluate() -> None:
    from modding.problem.evaluation import evaluate_problem as subject
    from modding.problem import models

    evaluation = subject.evaluate(
        copy.deepcopy(MOCK_PROBLEM_EVALUATION),
        MOCK_PROBLEM_EVALUATION_ID,
        MOCK_FILE_INPUT,
    )

    assert evaluation.id == MOCK_PROBLEM_EVALUATION_ID
    assert evaluation.veredict == models.ProblemVeredict.SENT.value
    assert evaluation.username == MOCK_PROBLEM_EVALUATION.get("username")
    assert evaluation.problem_id == MOCK_PROBLEM_EVALUATION.get("problem_id")


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch("modding.problem.evaluation.evaluate_problem.send_input_to_analyze")
def test_evaluate_not_sent_to_analizer(send_input_to_analyze: Mock) -> None:
    from modding.problem.evaluation import evaluate_problem as subject
    from modding.problem import models

    send_input_to_analyze.return_value = False

    with pytest.raises(subject.FileInputNotSentError):
        evaluation = subject.evaluate(
            copy.deepcopy(MOCK_PROBLEM_EVALUATION),
            MOCK_PROBLEM_EVALUATION_ID,
            MOCK_FILE_INPUT,
        )


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch("modding.problem.repository.ProblemRepository.get_item_by_id")
def test_build_evaluation(get_item_by_id: Mock) -> None:
    from modding.problem.evaluation import evaluate_problem as subject
    from modding.problem import models

    mock_evaluation_data = copy.deepcopy(MOCK_PROBLEM_EVALUATION)
    mock_evaluation_data.update(
        {
            "id": AnyStr(),
            "problem_id": AnyStr(),
            "veredict": models.ProblemVeredict.SENT,
        }
    )

    get_item_by_id.return_value = models.Problem.parse_obj(MOCK_PROBLEM)

    mock_evaluation = models.ProblemEvaluation.parse_obj(mock_evaluation_data)

    evaluation = subject.build_evaluation(
        **{**MOCK_PROBLEM_EVALUATION, "file_input": MOCK_FILE_INPUT}
    )

    assert (
        len(evaluation.id)
        > len(MOCK_PROBLEM_EVALUATION.get("problem_id")) + subject.EVALUATION_ID_LENGTH
    )
    assert mock_evaluation == evaluation


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch("modding.problem.repository.ProblemRepository.get_item_by_id")
@patch("modding.common.repo.Repository.save_on_table")
def test_evaluate_problem(save_on_table: Mock, get_item_by_id: Mock) -> None:
    from modding.problem import models
    from modding.problem.evaluation import evaluate_problem as subject

    mock_evaluation_data = copy.deepcopy(MOCK_PROBLEM_EVALUATION)
    mock_evaluation_data.update(
        {
            "id": AnyStr(),
            "problem_id": AnyStr(),
            "veredict": models.ProblemVeredict.SENT,
        }
    )

    get_item_by_id.return_value = models.Problem.parse_obj(MOCK_PROBLEM)

    mock_evaluation = models.ProblemEvaluation.parse_obj(mock_evaluation_data)

    evaluation = subject.evaluate_problem(
        **{**MOCK_PROBLEM_EVALUATION, "file_input": MOCK_FILE_INPUT}
    )

    assert evaluation == mock_evaluation
    save_on_table.assert_called_once_with(mock_evaluation)
