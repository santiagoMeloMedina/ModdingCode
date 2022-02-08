import pydantic


class Model(pydantic.BaseModel):
    id: str
    visible: bool = False
