from src.commons import entities
from singleton_injector import injector
from src.commons.http import HttpMethods
from src.problem import stack, lambdas


@injector
class ProblemRestApi(entities.LambdaRestApi):
    def __init__(
        self, scope: stack.ProblemStack, create_problem: lambdas.CreateProblemLambda
    ):
        super().__init__(scope=scope, id="ProblemRestApi", name="ProblemRestApi")

        self.main_resource = self.root.add_resource("problem")

        self.add_method(
            self.main_resource,
            method=HttpMethods.POST,
            integration_lambda=create_problem,
        )
