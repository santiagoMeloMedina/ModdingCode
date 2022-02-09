import os
from unittest.mock import patch, Mock
import pytest


class AnyStr(str):
    def __eq__(self, *args, **kwargs):
        return True


MOCK_MINICOURSE_ID = "prefix-aaaaa"
MULTIPLE_MINICOURSE_RETRIVAL_LIMIT = "10"

_DEFAULT_ENVIRONMENT = {
    "MINICOURSE_BUCKET_NAME": "",
    "MINICOURSE_TABLE_NAME": "",
    "THUMB_DOWNLOAD_EXPIRE_TIME": "300",
    "THUMB_UPLOAD_EXPIRE_TIME": "300",
    "MULTIPLE_MINICOURSE_RETRIVAL_LIMIT": MULTIPLE_MINICOURSE_RETRIVAL_LIMIT,
}

MOCK_MINICOURSE_THUMB_UPLOAD_URL = "http://thumb"
MOCK_MINICOURSE_THUMB_DOWNLOAD_URL = "http://thumb2"


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch(
    "modding.common.repo.Repository.get_presigned_url",
    return_value=MOCK_MINICOURSE_THUMB_DOWNLOAD_URL,
)
@patch("modding.minicourse.repository.MinicourseRepository.get_item_by_id")
def test_get_single_minicourse(
    minicourse_get_item_by_id: Mock, get_presigned_url: Mock
) -> None:
    from modding.minicourse import get_minicourse as subject, models

    MOCK_MINICOURSE = models.Minicourse(
        id=MOCK_MINICOURSE_ID, name=AnyStr(), category_id=AnyStr(), ext=AnyStr()
    )

    minicourse_get_item_by_id.return_value = MOCK_MINICOURSE

    result = subject.get_minicourse(id=MOCK_MINICOURSE_ID, get_thumb=True)

    minicourse_get_item_by_id.assert_called_once_with(MOCK_MINICOURSE_ID)
    assert "minicourse" in result
    assert "thumb_download_url" in result
    assert MOCK_MINICOURSE == result.get("minicourse")
    assert MOCK_MINICOURSE_THUMB_DOWNLOAD_URL == result.get("thumb_download_url")


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch(
    "modding.common.repo.Repository.get_presigned_url",
    return_value=MOCK_MINICOURSE_THUMB_DOWNLOAD_URL,
)
@patch("modding.minicourse.repository.MinicourseRepository.get_item_by_id")
def test_get_single_minicourse_no_thumbnail(
    minicourse_get_item_by_id: Mock, get_presigned_url: Mock
) -> None:
    from modding.minicourse import get_minicourse as subject, models

    MOCK_MINICOURSE = models.Minicourse(
        id=MOCK_MINICOURSE_ID, name=AnyStr(), category_id=AnyStr(), ext=AnyStr()
    )

    minicourse_get_item_by_id.return_value = MOCK_MINICOURSE

    result = subject.get_minicourse(id=MOCK_MINICOURSE_ID, get_thumb=False)

    minicourse_get_item_by_id.assert_called_once_with(MOCK_MINICOURSE_ID)
    assert "minicourse" in result
    assert "thumb_download_url" not in result
    assert MOCK_MINICOURSE == result.get("minicourse")


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch(
    "modding.common.repo.Repository.get_presigned_url",
    return_value=MOCK_MINICOURSE_THUMB_DOWNLOAD_URL,
)
@patch("modding.minicourse.get_minicourse.get_minicourse")
def test_get_multiple_minicourses(
    get_minicourse: Mock, get_presigned_url: Mock
) -> None:
    from modding.minicourse import get_minicourse as subject

    MULTIPLE_LIMIT = int(MULTIPLE_MINICOURSE_RETRIVAL_LIMIT)

    subject.get_multiple_minicourses(
        [MOCK_MINICOURSE_ID for _ in range(MULTIPLE_LIMIT)]
    )

    assert get_minicourse.call_count == MULTIPLE_LIMIT


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch(
    "modding.common.repo.Repository.get_presigned_url",
    return_value=MOCK_MINICOURSE_THUMB_DOWNLOAD_URL,
)
@patch("modding.minicourse.get_minicourse.get_minicourse")
def test_get_multiple_minicourses_too_many(
    get_minicourse: Mock, get_presigned_url: Mock
) -> None:
    from modding.minicourse import get_minicourse as subject

    MULTIPLE_LIMIT = 20

    with pytest.raises(subject.TooManyMinicoursesRetrival):
        subject.get_multiple_minicourses(
            [MOCK_MINICOURSE_ID for _ in range(MULTIPLE_LIMIT)]
        )


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch(
    "modding.common.repo.Repository.put_presigned_url",
    return_value=MOCK_MINICOURSE_THUMB_UPLOAD_URL,
)
@patch("modding.minicourse.get_minicourse.get_minicourse")
def test_get_minicourse_thumb_upload_url(
    get_minicourse: Mock, put_presigned_url: Mock
) -> None:
    from modding.minicourse import get_minicourse as subject

    result = subject.get_minicourse_thumb_upload_url(MOCK_MINICOURSE_ID)

    assert "thumb_upload_url" in result
    assert result.get("thumb_upload_url") == MOCK_MINICOURSE_THUMB_UPLOAD_URL


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch("modding.minicourse.get_minicourse.get_minicourse", return_value=1)
@patch("modding.minicourse.get_minicourse.get_multiple_minicourses", return_value=2)
@patch(
    "modding.minicourse.get_minicourse.get_minicourse_thumb_upload_url", return_value=3
)
def test_actions(
    get_minicourse_thumb_upload_url: Mock,
    get_multiple_minicourses: Mock,
    get_minicourse: Mock,
) -> None:
    from modding.minicourse import get_minicourse as subject

    assert subject.actions("get_minicourse", {}) == get_minicourse()
    assert (
        subject.actions("get_minicourse_thumb_upload_url", {})
        == get_minicourse_thumb_upload_url()
    )
    assert subject.actions("get_multiple_minicourses", {}) == get_multiple_minicourses()


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch("modding.minicourse.get_minicourse.get_minicourse")
@patch("modding.minicourse.get_minicourse.get_multiple_minicourses")
@patch("modding.minicourse.get_minicourse.get_minicourse_thumb_upload_url")
def test_actions_no_registered_action(
    get_minicourse_thumb_upload_url: Mock,
    get_multiple_minicourses: Mock,
    get_minicourse: Mock,
) -> None:
    from modding.minicourse import get_minicourse as subject

    assert subject.actions("get_any_minicourse", {}) == None
