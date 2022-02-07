from aws_cdk.aws_dynamodb import Attribute, AttributeType
from src.commons import entities
from singleton_injector import injector
from src.minicourse import stack as minicourse_stack


######################################
##           S3 BUCKETS             ##
######################################


@injector
class MinicourseBucket(entities.Bucket):
    def __init__(self, scope: minicourse_stack.MinicourseStack):
        super().__init__(scope=scope, id="MinicourseBucket", entity_name="Minicourse")


######################################
##         DYNAMODB TABLES          ##
######################################


@injector
class MinicourseTable(entities.Table):
    def __init__(self, scope: minicourse_stack.MinicourseStack):
        super().__init__(
            scope=scope,
            entity_name="Minicourse",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
        )

        self.add_secundary_index(
            partition_key=Attribute(name="category_id", type=AttributeType.STRING)
        )


@injector
class CategoryTable(entities.Table):
    def __init__(self, scope: minicourse_stack.MinicourseStack):
        super().__init__(
            scope=scope,
            entity_name="Category",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
        )
