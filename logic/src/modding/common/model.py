from typing import Optional
import pydantic


class Model(pydantic.BaseModel):
    id: str
    visible: bool = False
    creation_date: Optional[str]


class ModelShown(pydantic.BaseModel):
    id: str
    creation_date: Optional[str]
