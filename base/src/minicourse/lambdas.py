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
                "MINICOURSE_BUCKET_NAME": minicourse_bucket.bucket_name,
                "MINICOURSE_TABLE_NAME": minicourse_table.table_name,
                "CATEGORY_TABLE_NAME": category_table.table_name,
                "THUMB_UPLOAD_EXPIRE_TIME": "300",
            },
        )

        self.grant_table(table=minicourse_table, read=True, write=True)
        self.grant_table(table=category_table, read=True)
        self.grant_bucket(minicourse_bucket, read=True, write=True)
