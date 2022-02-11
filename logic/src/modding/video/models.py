import enum
from typing import Optional
from modding.common import model


class VideoSections(enum.Enum):
    CONTEXT = "CONTEXT"
    PREPARATION = "PREPARATION"
    CONTENT = "CONTENT"
    EXAMPLES = "EXAMPLES"
    FINISHING_UP = "FINISHING_UP"


class Video(model.Model):
    name: str
    ext: str
    minicourse_id: str
    section: VideoSections
    order: Optional[int]

    class Config:
        use_enum_values = True
