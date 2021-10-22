from aws_cdk.aws_dynamodb import Attribute, AttributeType
from src import stacks
from src.tables import Table
from singleton_injector import injector


@injector
class VideoTable(Table):
    def __init__(self, scope: stacks.VideoStack):
        super().__init__(
            scope=scope,
            id="VideoDynamoDBTable",
            name="VideoTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
        )
