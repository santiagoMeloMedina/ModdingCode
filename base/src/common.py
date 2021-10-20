import pydash
from pydantic import BaseSettings
from aws_cdk import core


class _Settings(BaseSettings):
    aws_region: str = "us-east-1"
    aws_account: str = "123324324"


class Singletons:
    def __init__(self):
        self.__instances = {}

    def __call__(self, _class, *args, **kwargs):
        class_id = pydash.get(_class, "class_id", default=_class)
        if class_id not in self.__instances:
            self.__instances[class_id] = _class(*args, **kwargs)
        return self.__instances[class_id]

    def get_instances(self):
        print(self.__instances, sep="\n")


SINGLETONS = Singletons()

_SETTINGS = _Settings()

ENVIRONMENT = core.Environment(
    account=_SETTINGS.aws_account, region=_SETTINGS.aws_region
)

app = core.App()
