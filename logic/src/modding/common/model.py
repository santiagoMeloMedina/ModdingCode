from typing import Optional
import pydantic


class Model(pydantic.BaseModel):
    id: str
    visible: bool = False
    creation_date: Optional[str]
