from singleton_injector import injector
from src.commons import entities
from src.problem import stack, storage
from src.minicourse import storage as minicourse_storage


### PARAMS ###


@injector
class EvaluationInstancePrivateKeyParam(entities.SecureStringParam):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(
            scope=scope,
            id="EvaluationInstancePrivateKeyParam",
            path="/ec2/private_key",
            env_name="INSTANCE_PRIVATE_KEY",
        )


@injector
class EvaluationInstancePublicDNSParam(entities.SecureStringParam):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(
            scope=scope,
            id="EvaluationInstancePublicDNSParam",
            path="/ec2/public_dns",
            env_name="INSTANCE_PUBLIC_DNS",
        )


@injector
class EvaluationInstanceUsernameParam(entities.SecureStringParam):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(
            scope=scope,
            id="EvaluationInstanceUsernameParam",
            path="/ec2/username",
            env_name="INSTANCE_USERNAME",
        )


@injector
class Auth0DomainParam(entities.SecureStringParam):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(
            scope=scope,
            id="Auth0DomainParam",
            path="/auth0/domain",
            env_name="AUTH0_DOMAIN",
        )


@injector
class Auth0ClientIDParam(entities.SecureStringParam):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(
            scope=scope,
            id="Auth0ClientIDParam",
            path="/auth0/client_id",
            env_name="AUTH0_CLIENT_ID",
        )


@injector
class Auth0ClientSecretParam(entities.SecureStringParam):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(
            scope=scope,
            id="Auth0ClientSecretParam",
            path="/auth0/client_secret",
            env_name="AUTH0_CLIENT_SECRET",
        )


@injector
class Auth0AudienceParam(entities.SecureStringParam):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(
            scope=scope,
            id="Auth0AudienceParam",
            path="/auth0/audience",
            env_name="AUTH0_AUDIENCE",
        )


@injector
class Auth0ExpertRoleParam(entities.SecureStringParam):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(
            scope=scope,
            id="Auth0ExpertRoleParam",
            path="/auth0/role/expert",
            env_name="EXPERT_ROLE_ID",
        )


@injector
class Auth0StudentRoleParam(entities.SecureStringParam):
    def __init__(self, scope: stack.ProblemStack):
        super().__init__(
            scope=scope,
            id="Auth0StudentRoleParam",
            path="/auth0/role/student",
            env_name="STUDENT_ROLE_ID",
        )


### LAMBDAS ###


@injector
class CreateProblemLambda(entities.Lambda):
    def __init__(
        self,
        scope: stack.ProblemStack,
        problem_table: storage.ProblemTable,
        problem_bucket: storage.ProblemBucket,
        minicourse_table: minicourse_storage.MinicourseTable,
    ):
        super().__init__(
            scope=scope,
            id="CreateProblemLambda",
            source="modding/problem/create_problem",
            env={
                **problem_table.get_env_name_var(),
                **problem_bucket.get_env_name_var(),
                **minicourse_table.get_env_name_var(),
            },
        )

        self.grant_table(table=problem_table, read=True, write=True)
        self.grant_table(table=minicourse_table, read=True, write=True)
        self.grant_bucket(problem_bucket, read=True, write=True)


@injector
class CreateProblemEvaluationLambda(entities.Lambda):
    def __init__(
        self,
        scope: stack.ProblemStack,
        problem_table: storage.ProblemTable,
        problem_bucket: storage.ProblemBucket,
        problem_evaluation_table: storage.ProblemEvaluationTable,
        instance_username: EvaluationInstanceUsernameParam,
        instance_public_dns: EvaluationInstancePublicDNSParam,
        instance_private_key: EvaluationInstancePrivateKeyParam,
    ):
        super().__init__(
            scope=scope,
            id="CreateProblemEvaluationLambda",
            source="modding/problem/evaluation/evaluate_problem",
            env={
                **problem_table.get_env_name_var(),
                **problem_bucket.get_env_name_var(),
                **problem_evaluation_table.get_env_name_var(),
                instance_username.env_name: instance_username.path,
                instance_public_dns.env_name: instance_public_dns.path,
                instance_private_key.env_name: instance_private_key.path,
            },
            timeout_seconds=60,
        )

        self.grant_table(table=problem_table, read=True, write=True)
        self.grant_bucket(problem_bucket, read=True, write=True)
        self.grant_table(table=problem_evaluation_table, read=True, write=True)

        self.grant_param(instance_username, read=True)
        self.grant_param(instance_public_dns, read=True)
        self.grant_param(instance_private_key, read=True)


@injector
class DeleteProblemLambda(entities.Lambda):
    def __init__(
        self,
        scope: stack.ProblemStack,
        problem_table: storage.ProblemTable,
    ):
        super().__init__(
            scope=scope,
            id="DeleteProblemLambda",
            source="modding/problem/delete_problem",
            env={**problem_table.get_env_name_var()},
        )

        self.grant_table(table=problem_table, read=True, write=True)


@injector
class UpdateProblemLambda(entities.Lambda):
    def __init__(
        self,
        scope: stack.ProblemStack,
        problem_table: storage.ProblemTable,
    ):
        super().__init__(
            scope=scope,
            id="UpdateProblemLambda",
            source="modding/problem/update_problem",
            env={**problem_table.get_env_name_var()},
        )

        self.grant_table(table=problem_table, read=True, write=True)


@injector
class GetProblemLambda(entities.Lambda):
    def __init__(
        self,
        scope: stack.ProblemStack,
        problem_table: storage.ProblemTable,
    ):
        super().__init__(
            scope=scope,
            id="GetProblemLambda",
            source="modding/problem/get_problem",
            env={**problem_table.get_env_name_var(), **problem_table.get_index_names()},
        )

        self.grant_table(table=problem_table, read=True, write=True)


@injector
class GetEvaluationLambda(entities.Lambda):
    def __init__(
        self,
        scope: stack.ProblemStack,
        evaluation_table: storage.ProblemEvaluationTable,
    ):
        super().__init__(
            scope=scope,
            id="GetEvaluationLambda",
            source="modding/problem/evaluation/get_evaluation",
            env={
                **evaluation_table.get_env_name_var(),
                **evaluation_table.get_index_names(),
            },
        )

        self.grant_table(table=evaluation_table, read=True, write=True)


@injector
class UploadProblemTestCaseLambda(entities.Lambda):
    def __init__(
        self,
        scope: stack.ProblemStack,
        problem_table: storage.ProblemTable,
        problem_bucket: storage.ProblemBucket,
    ):
        super().__init__(
            scope=scope,
            id="UploadProblemTestCaseLambda",
            source="modding/problem/upload_test_cases",
            env={
                **problem_table.get_env_name_var(),
                **problem_bucket.get_env_name_var(),
                "UPLOAD_URL_EXPIRE_TIME": "300",
            },
        )

        self.grant_table(table=problem_table, read=True, write=True)
        self.grant_bucket(problem_bucket, read=True, write=True)


@injector
class SendMessageToExpertLambda(entities.Lambda):
    def __init__(
        self,
        scope: stack.ProblemStack,
    ):
        super().__init__(
            scope=scope,
            id="SendMessageToExpertLambda",
            source="modding/problem/send_question",
            env={},
        )

        self.add_allow_policy(
            [entities.PolicyAction.SES_SEND, entities.PolicyAction.SES_SEND_RAW]
        )


@injector
class SendMessageToStudentLambda(entities.Lambda):
    def __init__(
        self,
        scope: stack.ProblemStack,
    ):
        super().__init__(
            scope=scope,
            id="SendMessageToStudentLambda",
            source="modding/problem/send_response",
            env={},
        )

        self.add_allow_policy(
            [entities.PolicyAction.SES_SEND, entities.PolicyAction.SES_SEND_RAW]
        )


@injector
class SignUpLambda(entities.Lambda):
    def __init__(
        self,
        scope: stack.ProblemStack,
        auth0_domain: Auth0DomainParam,
        auth0_client_id: Auth0ClientIDParam,
        auth0_client_secret: Auth0ClientSecretParam,
        auth0_audience: Auth0AudienceParam,
        expert_role: Auth0ExpertRoleParam,
        student_role: Auth0StudentRoleParam,
    ):
        super().__init__(
            scope=scope,
            id="SignUpLambda",
            source="modding/problem/signup",
            env={
                auth0_domain.env_name: auth0_domain.path,
                auth0_client_id.env_name: auth0_client_id.path,
                auth0_client_secret.env_name: auth0_client_secret.path,
                auth0_audience.env_name: auth0_audience.path,
                expert_role.env_name: expert_role.path,
                student_role.env_name: student_role.path,
            },
        )

        self.grant_param(auth0_domain, read=True)
        self.grant_param(auth0_client_id, read=True)
        self.grant_param(auth0_client_secret, read=True)
        self.grant_param(auth0_audience, read=True)
        self.grant_param(expert_role, read=True)
        self.grant_param(student_role, read=True)

        self.add_allow_policy(
            [
                entities.PolicyAction.SES_VERIFY_ADDRESS,
                entities.PolicyAction.SES_VERIFY_IDENTITY,
            ]
        )
