from re import A
from modding.common import aws_cli, exception, repo
from modding.problem import models
from modding.minicourse import models as minicourse_models


class ProblemRepository(repo.Repository):
    def __init__(self, table_name: str = str(), bucket_name: str = str()):
        super().__init__(name="Problem", table_name=table_name, bucket_name=bucket_name)
