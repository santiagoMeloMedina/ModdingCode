from re import A
from modding.common import aws_cli, exception, repo
from modding.problem import models
from modding.minicourse import models as minicourse_models


class ProblemRepository(repo.Repository):
    def __init__(
        self,
        table_name: str = str(),
        bucket_name: str = str(),
        minicourse_table_name: str = str(),
    ):
        super().__init__(name="Problem", table_name=table_name)

        self.minicourse_table = aws_cli.AwsCustomClient.dynamo(minicourse_table_name)
        self.s3 = aws_cli.AwsCustomClient.s3()
        self.bucket_name = bucket_name

    def get_problem_by_id(self, problem_id: str) -> models.Problem:
        try:
            if problem_id:
                data = self.table.get_item({"id": problem_id})
                if data is not None:
                    return models.Problem.parse_obj(data)
                else:
                    raise self.NotFoundProblemException(problem_id)
            else:
                raise self.NoIdProvided()
        except Exception as e:
            raise exception.LoggingException(e)

    def get_minicourse_by_id(self, minicourse_id: str) -> models.Problem:
        try:
            if minicourse_id:
                data = self.minicourse_table.get_item({"id": minicourse_id})
                if data is not None:
                    return minicourse_models.Minicourse.parse_obj(data)
                else:
                    raise self.NotFoundEntityException(minicourse_id)
            else:
                raise self.NoIdProvided()
        except Exception as e:
            raise exception.LoggingException(e)
