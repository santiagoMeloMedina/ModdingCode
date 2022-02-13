from aws_cdk.aws_dynamodb import Attribute, AttributeType
from src.commons import entities
from singleton_injector import injector
from src.video import stack as video_stack


######################################
##           S3 BUCKETS             ##
######################################


@injector
class VideoBucket(entities.Bucket):
    def __init__(self, scope: video_stack.VideoStack):
        super().__init__(scope=scope, id="VideoBucket", entity_name="Video")


######################################
##         DYNAMODB TABLES          ##
######################################


@injector
class VideoTable(entities.Table):
    def __init__(self, scope: video_stack.VideoStack):
        super().__init__(
            scope=scope,
            entity_name="Video",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
        )

        self.add_secundary_index(
            name="VideoMinicourse",
            partition_key=Attribute(name="minicourse_id", type=AttributeType.STRING),
            sort_key=Attribute(name="creation_date", type=AttributeType.NUMBER),
        )
