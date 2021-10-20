from typing import Optional
from aws_cdk import core, aws_dynamodb as _dynamodb


class Table(_dynamodb.Table):
    def __init__(
        self,
        scope: core.Construct,
        id: str,
        name: str,
        partition_key: _dynamodb.Attribute,
        sort_key: Optional[_dynamodb.Attribute] = None,
    ):
        super().__init__(
            scope=scope,
            id=id,
            table_name=name,
            partition_key=partition_key,
            sort_key=sort_key,
            billing_mode=_dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=_dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
        )
