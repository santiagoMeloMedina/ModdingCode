
import pytest

@pytest.mark.unit
def test_clean_extension_sucessful():
    from src.modding.utils import files as subject

    EXTENSION = "..,....,,.ext..,"

    cleaned = subject.clean_extension(EXTENSION)

    assert cleaned == "ext"
    