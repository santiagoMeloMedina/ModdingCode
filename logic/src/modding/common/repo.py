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

    def __init__(self, name: str, table_name: str) -> None:
        self.NotFoundEntityException = lambda entity_id: self.__NotFoundEntityException(
            id=entity_id, entity=name
        )

        self.table = aws_cli.AwsCustomClient.dynamo(table_name)

    def __item_from_table_exists(self, entity_body: model.Model) -> bool:
        item = self.table.get_item({"id": entity_body.id})
        return item is not None

    def get_item_by_id(self, id: str) -> model.Model:
        item = self.table.get_item({"id": id})
        if item is not None:
            return item
        else:
            raise self.NotFoundEntityException(id)

    def save_on_table(self, entity_body: model.Model) -> None:
        if not self.__item_from_table_exists(entity_body):
            item = entity_body.dict()
            item.update({"creation_date": date.get_unix_time_from_now()})
            self.table.put_item(item)
        else:
            raise self.NotSavingIdAlreadyExistsOnTableException(entity_body.id)
