from modding.common import repo
from modding.problem import models


class ProblemRepository(repo.Repository):
    def __init__(self, table_name: str = str(), bucket_name: str = str()):
        super().__init__(name="Problem", table_name=table_name, bucket_name=bucket_name)

        self.set_model(models.Problem)
