import enum
from typing import Optional
import pydantic


class DataState(enum.Enum):
    ACTIVE = "ACTIVE"
    INACTIVE = "INACTIVE"


class CommonModel(pydantic.BaseModel):
    id: str
    creation_date: Optional[str]
    updated_date: Optional[str]
    data_state: DataState = DataState.ACTIVE
    username: Optional[str]

    class Config:
        use_enum_values = True


class Model(CommonModel):
    visible: bool = False


class ModelShown(CommonModel):
    id: str
