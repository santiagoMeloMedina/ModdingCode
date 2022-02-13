from asyncore import write
from singleton_injector import injector
from src.commons import entities
from src.minicourse import stack as minicourse_stack, storage as minicourse_storage


@injector
class CreateMinicourseLambda(entities.Lambda):
    def __init__(
        self,
        scope: minicourse_stack.MinicourseStack,
        minicourse_table: minicourse_storage.MinicourseTable,
        category_table: minicourse_storage.CategoryTable,
        minicourse_bucket: minicourse_storage.MinicourseBucket,
    ):
        super().__init__(
            scope=scope,
            id="CreateMinicourseLambda",
            source="modding/minicourse/create_minicourse",
            env={
                **minicourse_table.get_env_name_var(),
                **minicourse_bucket.get_env_name_var(),
                **category_table.get_env_name_var(),
                "THUMB_UPLOAD_EXPIRE_TIME": "300",
            },
        )

        self.grant_table(table=minicourse_table, read=True, write=True)
        self.grant_table(table=category_table, read=True)
        self.grant_bucket(minicourse_bucket, read=True, write=True)


@injector
class GetMinicourseLambda(entities.Lambda):
    def __init__(
        self,
        scope: minicourse_stack.MinicourseStack,
        minicourse_table: minicourse_storage.MinicourseTable,
        minicourse_bucket: minicourse_storage.MinicourseBucket,
    ):
        super().__init__(
            scope=scope,
            id="GetMinicourseLambda",
            source="modding/minicourse/get_minicourse",
            env={
                **minicourse_table.get_env_name_var(),
                **minicourse_bucket.get_env_name_var(),
                "THUMB_DOWNLOAD_EXPIRE_TIME": "300",
                "THUMB_UPLOAD_EXPIRE_TIME": "300",
                "MULTIPLE_MINICOURSE_RETRIVAL_LIMIT": "10",
            },
        )

        self.grant_table(table=minicourse_table, read=True, write=True)
        self.grant_bucket(minicourse_bucket, read=True, write=True)


@injector
class UpdateMinicourseLambda(entities.Lambda):
    def __init__(
        self,
        scope: minicourse_stack.MinicourseStack,
        minicourse_table: minicourse_storage.MinicourseTable,
    ):
        super().__init__(
            scope=scope,
            id="UpdateMinicourseLambda",
            source="modding/minicourse/update_minicourse",
            env={
                **minicourse_table.get_env_name_var(),
            },
        )

        self.grant_table(table=minicourse_table, read=True, write=True)


@injector
class CreateCategoryLamdba(entities.Lambda):
    def __init__(
        self,
        scope: minicourse_stack.MinicourseStack,
        category_table: minicourse_storage.CategoryTable,
    ):
        super().__init__(
            scope=scope,
            id="CreateCategoryLamdba",
            source="modding/minicourse/category/create_category",
            env={
                **category_table.get_env_name_var(),
            },
        )

        self.grant_table(table=category_table, read=True, write=True)


@injector
class GetCategoriesLambda(entities.Lambda):
    def __init__(
        self,
        scope: minicourse_stack.MinicourseStack,
        category_table: minicourse_storage.CategoryTable,
    ):
        super().__init__(
            scope=scope,
            id="GetCategoriesLambda",
            source="modding/minicourse/category/get_category",
            env={**category_table.get_env_name_var()},
        )

        self.grant_table(table=category_table, read=True, write=True)


@injector
class DeleteCategoryLambda(entities.Lambda):
    def __init__(
        self,
        scope: minicourse_stack.MinicourseStack,
        category_table: minicourse_storage.CategoryTable,
    ):
        super().__init__(
            scope=scope,
            id="DeleteCategoryLambda",
            source="modding/minicourse/category/delete_category",
            env={**category_table.get_env_name_var()},
        )

        self.grant_table(table=category_table, read=True, write=True)
