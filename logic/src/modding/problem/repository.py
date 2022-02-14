from modding.common import repo
from modding.problem import models


class ProblemRepository(repo.Repository):

    FILES_PATH = "cases"

    def __init__(self, table_name: str = str(), bucket_name: str = str()):
        super().__init__(name="Problem", table_name=table_name, bucket_name=bucket_name)

        self.set_model(models.Problem)

    def file_put_presigned_url(self, file_id: str, expire_time: int) -> str:
        return self.put_presigned_url(self.FILES_PATH, file_id, expire_time)
