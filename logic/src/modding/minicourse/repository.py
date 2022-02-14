from typing import List
from modding.common import repo
from modding.minicourse import models


class MinicourseRepository(repo.Repository):

    THUMBNAILS_PATH = "thumbs"

    def __init__(self, table_name: str = str(), bucket_name: str = str()):
        super().__init__(
            name="Minicourse", table_name=table_name, bucket_name=bucket_name
        )

        self.set_model(models.Minicourse)

    def thumb_put_presigned_url(self, thumb_id: str, expire_time: int) -> str:
        return self.put_presigned_url(self.THUMBNAILS_PATH, thumb_id, expire_time)

    def thumb_get_presigned_url(self, thumb_id: str, expire_time: int) -> str:
        return self.get_presigned_url(self.THUMBNAILS_PATH, thumb_id, expire_time)

    def query_by_username(self, username_index_name: str) -> List[models.Minicourse]:
        keys = {"username": self._username}
        return self.query_items(keys, index_name=username_index_name)
