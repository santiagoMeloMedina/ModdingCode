import os
from pydantic import BaseSettings
from aws_cdk import core


class _Settings(BaseSettings):
    aws_region: str
    aws_account: str


_SETTINGS = _Settings()


environment = core.Environment(
    account=_SETTINGS.aws_account, region=_SETTINGS.aws_region
)

app = core.App()


def __get_path(folder: str) -> str:
    commons = os.path.dirname(__file__)
    src = os.path.dirname(commons)
    base = os.path.dirname(src)
    modding = os.path.dirname(base)
    logic = f"{modding}/logic"

    paths = {"base": base, "modding": modding, "logic": logic}

    return paths[folder]


LOGIC_SRC_PATH = f"{__get_path('logic')}/src"
LOGIC_LIBS_PATH = f"{__get_path('logic')}/artifacts/.libs.zip"
