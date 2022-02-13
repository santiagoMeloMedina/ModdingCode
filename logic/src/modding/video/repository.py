from modding.common import repo
from modding.video import models


class VideoRepository(repo.Repository):
    def __init__(self, table_name: str = str(), bucket_name: str = str()):
        super().__init__("Video", table_name=table_name, bucket_name=bucket_name)

        self.set_model(models.Video)

    def video_presigned_url(self, video_id: str, expire_time: int) -> str:
        return self.put_presigned_url("video", video_id, expire_time)
