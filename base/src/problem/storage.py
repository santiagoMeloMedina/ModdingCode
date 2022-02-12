from aws_cdk.aws_dynamodb import Attribute, AttributeType
from src.commons import entities
from singleton_injector import injector
from src.problem import stack


######################################
##           S3 BUCKETS             ##
######################################


@injector
class ProblemBucket(entities.Bucket):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(scope=scope, id="ProblemBucket", entity_name="Problem")


######################################
##         DYNAMODB TABLES          ##
######################################


@injector
class ProblemTable(entities.Table):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(
            scope=scope,
            entity_name="Problem",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
        )

        self.add_secundary_index(
            partition_key=Attribute(name="minicourse_id", type=AttributeType.STRING)
        )


@injector
class ProblemEvaluationTable(entities.Table):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(
            scope=scope,
            entity_name="ProblemEvaluation",
            partition_key=Attribute(name="id", type=AttributeType.STRING),
        )

        self.add_secundary_index(
            partition_key=Attribute(name="username", type=AttributeType.STRING),
            sort_key=Attribute(name="problem_id", type=AttributeType.STRING),
        )
