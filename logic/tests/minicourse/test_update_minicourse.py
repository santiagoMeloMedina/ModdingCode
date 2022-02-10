import os
from unicodedata import name
from unittest.mock import patch, Mock
from more_itertools import side_effect
import pytest


class AnyStr(str):
    def __eq__(self, *args, **kwargs):
        return True


MOCK_MINICOURSE_ID = "prefix-aaaaa"
MOCK_MINICOURSE_NAME = "min1"
MOCK_CATEGORY_ID = "cat1"
MOCK_ext = "png"

_DEFAULT_ENVIRONMENT = {"MINICOURSE_TABLE_NAME": ""}


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch("modding.minicourse.repository.MinicourseRepository.get_item_by_id")
def test_build_updated_minicourse(minicourse_get_item_by_id: Mock) -> None:
    from modding.minicourse import update_minicourse as subject, models

    mock_minicourse = models.Minicourse(
        id=MOCK_MINICOURSE_ID,
        name=MOCK_MINICOURSE_NAME,
        category_id=MOCK_CATEGORY_ID,
        ext=MOCK_ext,
    )

    minicourse_get_item_by_id.return_value = mock_minicourse

    MOCK_NEW_ID = "PREFIX2"
    MOCK_NEW_NAME = "MIN2"
    MOCK_NEW_ext = "JPG"

    updated_minicourse = subject.build_updated_minicourse(
        MOCK_MINICOURSE_ID,
        id=MOCK_NEW_ID,
        name=MOCK_NEW_NAME,
        ext=MOCK_NEW_ext,
    )

    assert not (updated_minicourse.name == mock_minicourse.name)
    assert updated_minicourse.name == MOCK_NEW_NAME
    assert not (updated_minicourse.ext == mock_minicourse.ext)
    assert updated_minicourse.ext == MOCK_NEW_ext
    assert updated_minicourse.id == mock_minicourse.id
    assert updated_minicourse.category_id == mock_minicourse.category_id


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch(
    "modding.minicourse.repository.MinicourseRepository.get_item_by_id",
    side_effect=Exception,
)
def test_build_updated_minicourse_fail_to_find_minicourse(
    minicourse_get_item_by_id: Mock,
) -> None:
    from modding.minicourse import update_minicourse as subject, models

    mock_minicourse = models.Minicourse(
        id=MOCK_MINICOURSE_ID,
        name=MOCK_MINICOURSE_NAME,
        category_id=MOCK_CATEGORY_ID,
        ext=MOCK_ext,
    )

    minicourse_get_item_by_id.return_value = mock_minicourse

    MOCK_NEW_NAME = "MIN2"

    with pytest.raises(subject.MinicourseNotBuilt):
        updated_minicourse = subject.build_updated_minicourse(
            MOCK_MINICOURSE_ID, name=MOCK_NEW_NAME
        )


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch("modding.minicourse.repository.MinicourseRepository.get_item_by_id")
@patch("modding.minicourse.repository.MinicourseRepository.save_on_table")
def test_update_minicourse_save(
    save_on_table: Mock, minicourse_get_item_by_id: Mock
) -> None:
    from modding.minicourse import update_minicourse as subject, models

    mock_minicourse = models.Minicourse(
        id=MOCK_MINICOURSE_ID,
        name=MOCK_MINICOURSE_NAME,
        category_id=AnyStr(),
        ext=AnyStr(),
    )

    minicourse_get_item_by_id.return_value = mock_minicourse

    updated_minicourse = subject.update_minicourse(MOCK_MINICOURSE_ID)

    save_on_table.assert_called_once_with(mock_minicourse, update=True)
