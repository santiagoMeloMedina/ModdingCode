from src import stacks, lambdas
from singleton_injector import injector


@injector
class SaveVideoLambdas(lambdas.LocalLambda):
    def __init__(self, scope: stacks.VideoStack):
        super().__init__(
            scope=scope,
            id="SaveVideoLambdas",
            source="src/hey",
            env={"hello": "hi"},
        )
