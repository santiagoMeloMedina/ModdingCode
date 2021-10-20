from aws_cdk import core
from src import common
from src.common import SINGLETONS as singleton
from src.common import app as main_project_app


class Stack(core.Stack):
    def __init__(self, id: str, name: str):
        super().__init__(
            scope=main_project_app, id=id, stack_name=name, env=common.ENVIRONMENT
        )


@singleton
class VideoStack(Stack):
    def __init__(self):
        super().__init__(id="VideoStack", name="VideoStack")
