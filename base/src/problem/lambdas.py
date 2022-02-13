from singleton_injector import injector
from src.commons import entities
from src.problem import stack, storage
from src.minicourse import storage as minicourse_storage


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
        problem_evaluation_table: storage.ProblemEvaluationTable,
    ):
        super().__init__(
            scope=scope,
            id="CreateProblemEvaluationLambda",
            source="modding/problem/evaluation/evaluate_problem",
            env={
                **problem_table.get_env_name_var(),
                **problem_evaluation_table.get_env_name_var(),
            },
        )

        self.grant_table(table=problem_table, read=True, write=True)
        self.grant_table(table=problem_evaluation_table, read=True, write=True)


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
