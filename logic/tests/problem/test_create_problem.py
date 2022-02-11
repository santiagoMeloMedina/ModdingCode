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
    "MINICOURSE_TABLE_NAME": "",
}

MOCK_PROBLEM_ID = "prefix-12341"
MOCK_PROBLEM_ESSENTIALS = {"name": "problem1", "minicourse_id": "min1", "difficulty": 1}


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
def test_build() -> None:
    from modding.problem import create_problem as subject, models

    problem = subject.build(copy.deepcopy(MOCK_PROBLEM_ESSENTIALS), MOCK_PROBLEM_ID)

    assert problem.id == MOCK_PROBLEM_ID
    assert problem.status == models.ProblemStatus.CREATED.value
    assert problem.name == MOCK_PROBLEM_ESSENTIALS.get("name")
    assert problem.minicourse_id == MOCK_PROBLEM_ESSENTIALS.get("minicourse_id")
    assert problem.difficulty == MOCK_PROBLEM_ESSENTIALS.get("difficulty")


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
def test_build_with_generator() -> None:
    from modding.problem import create_problem as subject, models

    mock_problem_data = copy.deepcopy(MOCK_PROBLEM_ESSENTIALS)
    mock_problem_data.update({"id": AnyStr(), "status": models.ProblemStatus.CREATED})

    mock_problem = models.Problem.parse_obj(mock_problem_data)

    problem = subject.build_problem(**MOCK_PROBLEM_ESSENTIALS)

    assert (
        len(problem.id)
        > len(MOCK_PROBLEM_ESSENTIALS.get("minicourse_id")) + subject.PROBLEM_ID_LENGTH
    )
    assert mock_problem == problem


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch("modding.common.repo.Repository.save_on_table")
def test_create_problem(save_on_table: Mock) -> None:
    from modding.problem import create_problem as subject, models

    mock_problem_data = copy.deepcopy(MOCK_PROBLEM_ESSENTIALS)
    mock_problem_data.update({"id": AnyStr(), "status": models.ProblemStatus.CREATED})

    mock_problem = models.Problem.parse_obj(mock_problem_data)

    problem = subject.create_problem(**MOCK_PROBLEM_ESSENTIALS)

    assert problem == mock_problem
    save_on_table.assert_called_once_with(mock_problem)
