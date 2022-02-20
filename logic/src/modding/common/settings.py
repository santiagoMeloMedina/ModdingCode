from typing import Any, Dict, Tuple
from pydantic import BaseSettings
from modding.common import aws_cli


SECURE_PREFIX = "_secure_"


class Settings(BaseSettings):
    def __init__(self, *args: Tuple[Any], **kwargs: Dict[str, Any]):
        super().__init__(*args, **kwargs)

        keys = self.dict()

        secure_params = dict()
        for key in keys:
            value = keys[key]
            if value and value.startswith(SECURE_PREFIX):
                secure_params[key] = value.replace(SECURE_PREFIX, "")

        self.__check_params(secure_params)

    def __check_params(self, keys: Dict[str, str]) -> None:
        for key in keys:
            value = keys[key]
            setattr(self, key, self.__get_param(value))

    def __get_param(self, param_value: str) -> str:
        try:
            ssm = aws_cli.AwsCustomClient.ssm()
            result = ssm.get_secure_params(param_value)
        except:
            result = param_value

        return result
