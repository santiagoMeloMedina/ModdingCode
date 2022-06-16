
import pytest

@pytest.mark.unit
def test_get_unix_time_returns_integer():
    from src.modding.utils import date as subject

    unix = subject.get_unix_time_from_now()

    assert type(unix) == int
    