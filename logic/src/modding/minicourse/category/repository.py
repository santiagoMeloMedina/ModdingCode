from modding.common import repo
from modding.minicourse import models


class CategoryRepository(repo.Repository):
    def __init__(self, table_name: str = str()):
        super().__init__(name="Category", table_name=table_name, bucket_name="")

        self.set_model(models.Category)
