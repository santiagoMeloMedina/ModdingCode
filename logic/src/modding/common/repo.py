from typing import Any, Dict
from modding.common import exception, aws_cli, model
from modding.utils import date


class Repository:
    class __NotFoundEntityException(exception.LoggingException):
        def __init__(self, id: str, entity: str):
            super().__init__("Can not find %s with the provided id %s" % (entity, id))

    class NoIdProvided(exception.LoggingException):
        def __init__(self):
            super().__init__("Did not provide an id")

    class NotSavingIdAlreadyExistsOnTableException(exception.LoggingException):
        def __init__(self, id: str):
            super().__init__(
                "Could not save id %s because already exists in table" % (id)
            )

    class S3PresigningError(exception.LoggingErrorException):
        def __init__(self, message: str):
            super().__init__("Can not get presigned url, %s" % (message))

    def __init__(self, name: str, table_name: str, bucket_name: str) -> None:
        self.NotFoundEntityException = lambda entity_id: self.__NotFoundEntityException(
            id=entity_id, entity=name
        )

        self.table = aws_cli.AwsCustomClient.dynamo(table_name)
        self.s3 = aws_cli.AwsCustomClient.s3(bucket_name)

    def __item_from_table_exists(self, entity_body: model.Model) -> bool:
        item = self.table.get_item({"id": entity_body.id})
        return item is not None

    def get_item_by_id(self, id: str) -> model.Model:
        item = self.table.get_item({"id": id})
        if item is not None:
            return item
        else:
            raise self.NotFoundEntityException(id)

    def put_presigned_url(self, path: str, id: str, expire_time: int) -> str:
        try:
            object_with_path = f"{path}/{id}"
            put_url = self.s3.put_file_presigned_url(
                object_name=object_with_path, expire=expire_time
            )
        except Exception as e:
            raise self.S3PresigningError(e)
        return put_url

    def get_presigned_url(self, path: str, id: str, expire_time: int) -> str:
        try:
            object_with_path = f"{path}/{id}"
            put_url = self.s3.get_file_presigned_url(
                object_name=object_with_path, expire=expire_time
            )
        except Exception as e:
            raise self.S3PresigningError(e)
        return put_url

    def save_on_table(self, entity_body: model.Model) -> None:
        if not self.__item_from_table_exists(entity_body):
            item = entity_body.dict()
            creation_date = date.get_unix_time_from_now()
            item.update(
                {
                    "creation_date": creation_date,
                    "id": f"{entity_body.id}-{creation_date}",
                }
            )
            self.table.put_item(item)
        else:
            raise self.NotSavingIdAlreadyExistsOnTableException(entity_body.id)
