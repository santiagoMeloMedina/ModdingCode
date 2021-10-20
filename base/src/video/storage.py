from aws_cdk.aws_dynamodb import Attribute, AttributeType
from src.common import SINGLETONS as singleton
from src.stacks import VideoStack
from src.tables import Table


@singleton
class VideoTable(Table):
    def __init__(self):
        super().__init__(
            scope=VideoStack,  # type: ignore
            id="VideoDynamoDBTable",
            name="VideoTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
        )
