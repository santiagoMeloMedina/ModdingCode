from aws_cdk import core
from src import common
from singleton_injector import injector


class Stack(core.Stack):
    def __init__(self, id: str, name: str):
        super().__init__(
            scope=common.app, id=id, stack_name=name, env=common.ENVIRONMENT
        )


@injector
class VideoStack(Stack):
    def __init__(self):
        super().__init__(id="VideoStack", name="VideoStack")
