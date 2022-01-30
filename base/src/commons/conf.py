import os
from pydantic import BaseSettings
from aws_cdk import core
from src.commons.file_finder import FileFinder


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


def get_excluded_files_from_logic(source_path: str):
    finder = FileFinder(f"{source_path}.py", LOGIC_SRC_PATH)
    excluded_files = [
        file.replace(f"{LOGIC_SRC_PATH}/", "")
        for file in finder.get_excluded_from_file()
    ]
    return excluded_files
