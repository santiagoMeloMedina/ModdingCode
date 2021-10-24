from typing import Optional
from pydantic import BaseSettings


class Settings(BaseSettings):
    common: Optional[str]
