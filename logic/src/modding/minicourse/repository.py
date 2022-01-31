from re import A
from modding.common import aws_cli, exception
from modding.minicourse import models as minicourse_models


class MinicourseRepository:
    class S3PresigningError(exception.LoggingErrorException):
        def __init__(self, message: str):
            super().__init__("Can not get presigned url, %s" % (message))

    class NoCategoryIdProvided(exception.LoggingException):
        def __init__(self):
            super().__init__("Did not provide a category id")

    class NotFoundCategoryException(exception.LoggingException):
        def __init__(self, id: str):
            super().__init__("Can not find category with the provided id %s" % (id))

    class MinicourseNotCreated(exception.LoggingException):
        def __init__(self, message: str):
            super().__init__("Could not create minicourse, %s" % (message))

    def __init__(
        self, minicourse_table_name: str, bucket_name: str, category_table_name: str
    ):
        self.minicourse_table = aws_cli.AwsCustomClient.dynamo(minicourse_table_name)
        self.category_table = aws_cli.AwsCustomClient.dynamo(category_table_name)
        self.s3 = aws_cli.AwsCustomClient.s3()

        self.bucket_name = bucket_name

    def get_thumb_put_presigned_url(self, thumb_id: str, expire_time: int) -> str:
        try:
            put_url = self.s3.put_file_presigned_url(
                bucket_name=self.bucket_name, object_name=thumb_id, expire=expire_time
            )
        except Exception as e:
            raise self.S3PresigningError(e)
        return put_url

    def get_category_by_id(self, category_id: str) -> minicourse_models.Category:
        try:
            if category_id:
                data = self.category_table.get_item({"id": category_id})
                if data is not None:
                    return minicourse_models.Category.parse_obj(data)
                else:
                    raise self.NotFoundCategoryException(category_id)
            else:
                raise self.NoCategoryIdProvided()
        except Exception as e:
            raise exception.LoggingException(e)

    def save_data(self, minicourse: minicourse_models.Minicourse) -> None:
        self.minicourse_table.put_item(item=minicourse.dict())
