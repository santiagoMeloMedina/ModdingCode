import pydantic
from modding.video.utils import date_format


class Video(pydantic.BaseModel):
    id: str
    name: str
    date: int = date_format.get_now_unix_time()
