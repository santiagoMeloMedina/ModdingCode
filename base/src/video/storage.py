from aws_cdk.aws_dynamodb import Attribute, AttributeType
from src.commons import entities
from singleton_injector import injector
from src.video import stack as video_stack


######################################
##           S3 BUCKETS             ##
######################################


@injector
class VideosBucket(entities.Bucket):
    def __init__(self, scope: video_stack.VideoStack):
        super().__init__(scope=scope, id="VideosBucket")


######################################
##         DYNAMODB TABLES          ##
######################################


@injector
class VideoTable(entities.Table):
    def __init__(self, scope: video_stack.VideoStack):
        super().__init__(
            scope=scope,
            id="VideoDynamoDBTable",
            name="VideoTable",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
        )
