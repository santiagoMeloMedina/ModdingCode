from src import stacks, lambdas


class SaveVideoLambdas(lambdas.LocalLambda):
    def __init__(self):
        super().__init__(
            scope=stacks.VideoStack,
            id="SaveVideoLambdas",
            source="src/hey",
            env={"hello": "hi"},
        )
