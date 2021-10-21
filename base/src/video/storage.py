from aws_cdk.aws_dynamodb import Attribute, AttributeType
from src import stacks
from src.tables import Table


class VideoTable(Table):
    def __init__(self):
        super().__init__(
            scope=stacks.VideoStack,  # type: ignore
            id="VideoDynamoDBTable",
            name="VideoTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
        )
