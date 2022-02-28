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
