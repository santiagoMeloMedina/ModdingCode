from typing import Optional
from modding.common import model


class Category(model.Model):
    name: str
    description: str


class Minicourse(model.Model):
    category_id: str
    name: str
    ext: str
    rate: Optional[int]
