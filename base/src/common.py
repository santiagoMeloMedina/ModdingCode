import os
from pydantic import BaseSettings
from aws_cdk import core


class _Settings(BaseSettings):
    aws_region: str
    aws_account: str


_SETTINGS = _Settings()

ENVIRONMENT = core.Environment(
    account=_SETTINGS.aws_account, region=_SETTINGS.aws_region
)

app = core.App()

BASE_PROJECT_FOLDER_PATH_STR = os.path.dirname(os.path.dirname(__file__))
GENERAL_PROJECTS_FOLDER_PATH_STR = os.path.dirname(BASE_PROJECT_FOLDER_PATH_STR)
LOGIC_PROJECT_FOLDER_PATH_STR = "/".join([GENERAL_PROJECTS_FOLDER_PATH_STR, "logic"])

LOGIC_PROJECT_FOLDER_ASSETS_PATH_STR = "%s/%s" % (
    LOGIC_PROJECT_FOLDER_PATH_STR,
    "assets",
)
