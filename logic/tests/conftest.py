from unittest.mock import patch
import pytest
import os
import sys


def naive_check_mark_exist(request, mark):
    marks = [m.name for m in request.node.iter_markers()]
    return mark in marks


@pytest.fixture(scope="function", autouse=True)
def modding_module() -> None:
    sys.path.insert(0, os.path.join("src", os.path.dirname(__name__)))


@pytest.fixture(scope="function", autouse=True)
def mock_aws_client(request, modding_module):
    import modding.common.aws_cli

    if not naive_check_mark_exist(request, "disable_aws_mock"):
        with patch.object(modding.common.aws_cli, "AwsCustomClient") as _fixture:
            yield _fixture
    else:
        yield
