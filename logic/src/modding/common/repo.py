import copy
from typing import Any, Dict, List
from modding.common import exception, aws_cli, model
from modding.utils import date


class Repository:
    class _NotFoundEntityException(exception.LoggingException):
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

    class UpdatingNotExistentEntity(exception.LoggingException):
        def __init__(self, id: str):
            super().__init__(
                "Could not update id %s because it does not exist in table" % (id)
            )

    class DeletingNotExistentEntity(exception.LoggingException):
        def __init__(self, id: str):
            super().__init__(
                "Could not delete id %s because it does not exist in table" % (id)
            )

    class S3PresigningError(exception.LoggingErrorException):
        def __init__(self, message: str):
            super().__init__("Can not get presigned url, %s" % (message))

    EQUAL_COMPARISON = "eq"

    def __init__(self, name: str, table_name: str, bucket_name: str) -> None:
        self.NotFoundEntityException = lambda entity_id: self._NotFoundEntityException(
            id=entity_id, entity=name
        )

        self.table = aws_cli.AwsCustomClient.dynamo(table_name)
        self.s3 = aws_cli.AwsCustomClient.s3(bucket_name)
        self.__model: model.Model = model.Model
        self._username: str = None

    def set_model(self, _model: model.Model) -> None:
        self.__model = _model

    def set_username(self, username: str) -> None:
        self._username = username

    def __get_item_by_id_no_exception(self, id: str) -> model.Model:
        item = self.table.get_item(
            {"id": id},
            {"data_state": (self.EQUAL_COMPARISON, model.DataState.ACTIVE.value)},
        )
        return self.__model.parse_obj(item) if item is not None else None

    def get_item_by_id(self, id: str) -> model.Model:
        item = self.__get_item_by_id_no_exception(id)
        if item is not None:
            return item
        else:
            raise self.NotFoundEntityException(id)

    def query_items(
        self, keys: Dict[str, Any], index_name: str = None
    ) -> List[model.Model]:
        result = []
        items = self.table.query_items(
            keys,
            {"data_state": (self.EQUAL_COMPARISON, model.DataState.ACTIVE.value)},
            index_name=index_name,
        )
        if items:
            result = [self.__model.parse_obj(item) for item in items]
        return result

    def query_items_by_username(
        self, keys: Dict[str, Any], index_name: str = None
    ) -> List[model.Model]:
        result = []
        items = self.table.query_items(
            keys,
            {
                "data_state": (self.EQUAL_COMPARISON, model.DataState.ACTIVE.value),
                "username": self._username,
            },
            index_name=index_name,
        )
        if items:
            result = [self.__model.parse_obj(item) for item in items]
        return result

    def scan_items(self, attr: Dict[str, Any]) -> List[model.Model]:
        result = []
        filters = copy.deepcopy(attr)
        filters.update(
            {"data_state": (self.EQUAL_COMPARISON, model.DataState.ACTIVE.value)}
        )
        items = self.table.scan_items(filters)
        if items:
            result = [self.__model.parse_obj(item) for item in items]
        return result

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

    def _create_data(self, entity: model.Model, current_date: int) -> None:
        extra_creation_data = {
            "id": f"{entity.id}-{current_date}",
            "creation_date": current_date,
            "username": self._username,
        }
        item = entity.dict()
        item.update(extra_creation_data)
        self.table.put_item(item)
        entity.id = extra_creation_data.get("id")
        entity.creation_date = extra_creation_data.get("creation_date")
        entity.username = extra_creation_data.get("username")

    def _update_data(self, entity: model.Model, current_date: int) -> None:
        extra_update_data = {"updated_date": current_date}
        item = entity.dict()
        item.update(extra_update_data)
        self.table.put_item(item)
        entity.updated_date = extra_update_data.get("updated_date")

    def save_on_table(self, entity: model.Model, update: bool = False) -> None:
        current_date = date.get_unix_time_from_now()
        if update:
            self._update_data(entity, current_date)
        else:
            self._create_data(entity, current_date)

    def delete_data(self, id: str) -> None:
        entity = self.__get_item_by_id_no_exception(id)
        if entity:
            item = entity.dict()
            item.update({"data_state": model.DataState.INACTIVE.value})
            self.table.put_item(item)
        else:
            raise self.DeletingNotExistentEntity(id)
