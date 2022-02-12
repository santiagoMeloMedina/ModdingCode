from modding.common import repo
from modding.problem import models


class ProblemEvaluationRepository(repo.Repository):
    def __init__(self, table_name: str = str(), bucket_name: str = str()):
        super().__init__(
            name="ProblemEvaluation", table_name=table_name, bucket_name=bucket_name
        )

        self.set_model(models.ProblemEvaluation)
