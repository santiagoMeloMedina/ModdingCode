import os
from unittest.mock import patch, Mock
import pytest


class AnyStr(str):
    def __eq__(self, *args, **kwargs) -> bool:
        return True


_DEFAULT_ENVIRONMENT = {
    "VIDEO_BUCKET_NAME": "",
    "VIDEO_TABLE_NAME": "",
    "UPLOAD_EXPIRE_TIME": "300",
}


MOCK_VIDEO_DATA = {"name": "test_video", "ext": ".__mp4", "minicourse_id": "min1"}

MOCK_VIDEO_ID = "prefix-1234"
MOCK_VIDEO_THUMB_UPLOAD_URL = "http://video"
MOCK_VIDEOS_FOLDER_NAME = "video"


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch(
    "modding.common.repo.Repository.put_presigned_url",
    return_value=MOCK_VIDEO_THUMB_UPLOAD_URL,
)
def test_build(put_presigned_url: Mock):
    from modding.video import create_video as subject, models
    from modding.utils import files

    mock_video_data = {
        **MOCK_VIDEO_DATA,
        "id": MOCK_VIDEO_ID,
        "section": models.VideoSections.CONTEXT,
    }

    video = subject.build(**mock_video_data)

    mock_video_data.update({"ext": files.clean_extension(mock_video_data.get("ext"))})

    assert models.Video(**mock_video_data) == video


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch(
    "modding.common.repo.Repository.put_presigned_url",
    return_value=MOCK_VIDEO_THUMB_UPLOAD_URL,
)
def test_build_with_generator(put_presigned_url: Mock):
    from modding.video import create_video as subject, models
    from modding.utils import files

    video = subject.build_video(
        **{
            **MOCK_VIDEO_DATA,
            "section": models.VideoSections.CONTEXT,
        }
    )

    assert len(video.id) > 0
    assert video.id.startswith(video.minicourse_id)

    mock_video = models.Video(
        id=AnyStr(),
        name=MOCK_VIDEO_DATA.get("name"),
        ext=files.clean_extension(MOCK_VIDEO_DATA.get("ext")),
        minicourse_id=MOCK_VIDEO_DATA.get("minicourse_id"),
        section=models.VideoSections.CONTEXT,
    )

    assert mock_video == video


@pytest.mark.unit
@patch.dict(os.environ, _DEFAULT_ENVIRONMENT)
@patch(
    "modding.common.repo.Repository.put_presigned_url",
    return_value=MOCK_VIDEO_THUMB_UPLOAD_URL,
)
@patch("modding.video.repository.VideoRepository.save_on_table")
def test_create_video(save_on_table: Mock, put_presigned_url: Mock):
    from modding.video import create_video as subject, models
    from modding.utils import files

    result = subject.create_video(
        **{
            **MOCK_VIDEO_DATA,
            "section": models.VideoSections.CONTEXT,
        }
    )

    mock_video = models.Video(
        id=AnyStr(),
        name=MOCK_VIDEO_DATA.get("name"),
        ext=files.clean_extension(MOCK_VIDEO_DATA.get("ext")),
        minicourse_id=MOCK_VIDEO_DATA.get("minicourse_id"),
        section=models.VideoSections.CONTEXT,
    )

    assert "video" in result
    assert "upload_url" in result
    assert result.get("upload_url") == MOCK_VIDEO_THUMB_UPLOAD_URL
    assert result.get("video") == mock_video

    save_on_table.assert_called_once_with(mock_video)
