from aws_cdk.aws_dynamodb import Attribute, AttributeType
from src import stacks, buckets
from src.tables import Table
from singleton_injector import injector


######################################
##           S3 BUCKETS             ##
######################################


@injector
class VideosBucket(buckets.Bucket):
    def __init__(self, scope: stacks.VideoStack):
        super().__init__(scope=scope, id="VideosBucket")


######################################
##         DYNAMODB TABLES          ##
######################################


@injector
class VideoTable(Table):
    def __init__(self, scope: stacks.VideoStack):
        super().__init__(
            scope=scope,
            id="VideoDynamoDBTable",
            name="VideoTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
        )
