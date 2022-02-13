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
        get_minicourse: minicourse_lambdas.GetMinicourseLambda,
        update_minicourse: minicourse_lambdas.UpdateMinicourseLambda,
        create_category: minicourse_lambdas.CreateCategoryLamdba,
        get_category: minicourse_lambdas.GetCategoriesLambda,
    ):
        super().__init__(scope=scope, id="MinicourseRestApi", name="MinicourseRestApi")

        self.main_resource = self.root.add_resource("minicourse")

        self.add_method(
            self.main_resource,
            method=HttpMethods.POST,
            integration_lambda=create_minicourse,
        )

        self.get_minicourse = self.main_resource.add_resource("get")

        self.add_method(
            self.get_minicourse,
            method=HttpMethods.POST,
            integration_lambda=get_minicourse,
        )

        self.add_method(
            self.main_resource,
            method=HttpMethods.PUT,
            integration_lambda=update_minicourse,
        )

        self.category_resource = self.main_resource.add_resource("category")

        self.add_method(
            self.category_resource,
            method=HttpMethods.POST,
            integration_lambda=create_category,
        )

        self.get_categories = self.category_resource.add_resource("get")

        self.add_method(
            self.get_categories,
            method=HttpMethods.POST,
            integration_lambda=get_category,
        )
