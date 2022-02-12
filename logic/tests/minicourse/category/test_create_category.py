import os
from typing import Any
from unittest.mock import Mock, patch
import pytest
import copy


class AnyStr(str):
    def __eq__(self, other: Any):
        return True


_DEFAULT_ENVIRONMENT = {
    "CATEGORY_TABLE_NAME": "",
}

MOCK_CATEGORY_ID = "prefix-12341"
MOCK_CATEGORY = {"name": "category1", "description": "category description"}


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
def test_build() -> None:
    from modding.minicourse.category import create_category as subject

    category = subject.build(**{**copy.deepcopy(MOCK_CATEGORY), "id": MOCK_CATEGORY_ID})

    assert category.id == MOCK_CATEGORY_ID
    assert category.name == MOCK_CATEGORY.get("name")
    assert category.description == MOCK_CATEGORY.get("description")


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
def test_build_with_id() -> None:
    from modding.minicourse.category import create_category as subject
    from modding.minicourse import models

    mock_category_data = copy.deepcopy(MOCK_CATEGORY)
    mock_category_data.update({"id": AnyStr()})

    mock_category = models.Category.parse_obj(mock_category_data)

    category = subject.build_with_id(**MOCK_CATEGORY)

    assert len(category.id) > subject.CATEGORY_ID_LENGTH
    assert mock_category == category


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch("modding.common.repo.Repository.save_on_table")
def test_create_category(save_on_table: Mock) -> None:
    from modding.minicourse import models
    from modding.minicourse.category import create_category as subject

    mock_category_data = copy.deepcopy(MOCK_CATEGORY)
    mock_category_data.update({"id": AnyStr()})

    mock_category = models.Category.parse_obj(mock_category_data)

    category = subject.create_category(**MOCK_CATEGORY)

    assert category == mock_category
    save_on_table.assert_called_once_with(mock_category)
