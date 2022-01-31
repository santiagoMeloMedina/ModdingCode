import pydantic


class Category(pydantic.BaseModel):
    id: str
    name: str


class Minicourse(pydantic.BaseModel):
    id: str
    category_id: str
    name: str
