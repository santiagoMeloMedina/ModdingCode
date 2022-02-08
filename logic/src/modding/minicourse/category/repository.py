from modding.common import repo


class CategoryRepository(repo.Repository):
    def __init__(self, table_name: str = str()):
        super().__init__(name="Category", table_name=table_name, bucket_name="")
