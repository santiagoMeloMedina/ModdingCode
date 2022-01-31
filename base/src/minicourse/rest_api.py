from src.commons import entities
from singleton_injector import injector
from src.commons.http import HttpMethods
from src.minicourse import stack as minicourse_stack, lambdas as minicourse_lambdas


@injector
class MinicourseRestApi(entities.LambdaRestApi):
    def __init__(
        self,
        scope: minicourse_stack.MinicourseStack,
        create_minicourse: minicourse_lambdas.CreateMinicourseLambda,
    ):
        super().__init__(scope=scope, id="MinicourseRestApi", name="MinicourseRestApi")

        self.main_resource = self.root.add_resource("minicourse")

        self.add_method(
            self.main_resource,
            method=HttpMethods.POST,
            integration_lambda=create_minicourse,
        )
