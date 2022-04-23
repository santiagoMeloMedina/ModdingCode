import enum
from src.commons import entities
from singleton_injector import injector
from src.commons.http import HttpMethods
from src.problem import stack, lambdas
from src.commons import security


class Scopes(enum.Enum):
    create_problem = "create/problem"
    get_problem = "get/problem"
    update_problem = "update/problem"
    delete_problem = "delete/problem"
    create_evaluation = "create/evaluation"
    get_evaluation = "get/evaluation"
    update_evaluation = "update/evaluation"
    delete_evaluation = "delete/evaluation"
    send_msg_as_expert = "send_msg/expert"
    send_msg_as_student = "send_msg/student"


@injector
class ProblemRestApi(entities.LambdaRestApi):
    def __init__(
        self,
        scope: stack.ProblemStack,
        create_problem: lambdas.CreateProblemLambda,
        evaluate_problem: lambdas.CreateProblemEvaluationLambda,
        delete_problem: lambdas.DeleteProblemLambda,
        update_problem: lambdas.UpdateProblemLambda,
        get_problem: lambdas.GetProblemLambda,
        get_evaluation: lambdas.GetEvaluationLambda,
        upload_test_case: lambdas.UploadProblemTestCaseLambda,
        send_message_to_expert: lambdas.SendMessageToExpertLambda,
        send_message_to_student: lambdas.SendMessageToStudentLambda,
    ):
        api_id = "ProblemRestApi"

        super().__init__(
            scope=scope,
            id=api_id,
            name=api_id,
            authorizer=security.Auth0Authorizer(scope, api_id),
        )

        self.main_resource = self.root.add_resource("problem")

        self.add_method(
            self.main_resource,
            method=HttpMethods.POST,
            integration_lambda=create_problem,
            roles=[Scopes.create_problem],
        )

        self.evaluation_resource = self.main_resource.add_resource("evaluation")

        self.add_method(
            self.evaluation_resource,
            method=HttpMethods.POST,
            integration_lambda=evaluate_problem,
            roles=[Scopes.create_evaluation],
        )

        self.add_method(
            self.main_resource,
            method=HttpMethods.DELETE,
            integration_lambda=delete_problem,
            roles=[Scopes.delete_problem],
        )

        self.add_method(
            self.main_resource,
            method=HttpMethods.PUT,
            integration_lambda=update_problem,
            roles=[Scopes.update_problem],
        )

        self.get_problem_resource = self.main_resource.add_resource("get")

        self.add_method(
            self.get_problem_resource,
            method=HttpMethods.POST,
            integration_lambda=get_problem,
            roles=[Scopes.get_problem],
        )

        self.get_evaluation_resource = self.evaluation_resource.add_resource("get")

        self.add_method(
            self.get_evaluation_resource,
            method=HttpMethods.POST,
            integration_lambda=get_evaluation,
            roles=[Scopes.get_evaluation],
        )

        self.test_case_resource = self.main_resource.add_resource("testcase")

        self.add_method(
            self.test_case_resource,
            method=HttpMethods.POST,
            integration_lambda=upload_test_case,
            roles=[Scopes.update_problem, Scopes.update_evaluation],
        )

        self.send_message = self.main_resource.add_resource("send-message")

        self.send_to_expert = self.send_message.add_resource("expert")

        self.add_method(
            self.send_to_expert,
            method=HttpMethods.POST,
            integration_lambda=send_message_to_expert,
            roles=[Scopes.send_msg_as_student],
        )

        self.send_to_student = self.send_message.add_resource("student")

        self.add_method(
            self.send_to_student,
            method=HttpMethods.POST,
            integration_lambda=send_message_to_student,
            roles=[Scopes.send_msg_as_expert],
        )

        self.authorizer.construct_roles()


@injector
class UserRestAPI(entities.LambdaRestApi):
    def __init__(
        self,
        scope: stack.ProblemStack,
        sign_up: lambdas.SignUpLambda,
    ):
        api_id = "UserRestAPI"

        super().__init__(scope=scope, id=api_id, name=api_id)

        self.main_resource = self.root.add_resource("user")

        self.signup_resource = self.main_resource.add_resource("signup")

        self.add_method(
            self.signup_resource,
            method=HttpMethods.POST,
            integration_lambda=sign_up,
        )
