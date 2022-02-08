from modding.common import repo


class MinicourseRepository(repo.Repository):

    THUMBNAILS_PATH = "thumbs"

    def __init__(self, table_name: str = str(), bucket_name: str = str()):
        super().__init__(
            name="Minicourse", table_name=table_name, bucket_name=bucket_name
        )

    def thumb_put_presigned_url(self, thumb_id: str, expire_time: int) -> str:
        return self.put_presigned_url(self.THUMBNAILS_PATH, thumb_id, expire_time)

    def thumb_get_presigned_url(self, thumb_id: str, expire_time: int) -> str:
        return self.get_presigned_url(self.THUMBNAILS_PATH, thumb_id, expire_time)
