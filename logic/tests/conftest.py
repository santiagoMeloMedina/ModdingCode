from unittest.mock import patch
import pytest
import os
import sys


@pytest.fixture(scope="session", autouse=True)
def modding_module() -> None:
    sys.path.insert(0, os.path.join("src", os.path.dirname(__name__)))


@pytest.fixture(scope="session", autouse=True)
def mock_aws_client(modding_module):
    import modding.common.aws_cli

    with patch.object(modding.common.aws_cli, "AwsCustomClient") as _fixture:
        yield _fixture
