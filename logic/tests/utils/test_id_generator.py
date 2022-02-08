import pytest

ENTITY_PREFIX = "prefix"
ENTITY_ID_LENGTH = 5


@pytest.mark.unit
def test_id_generator() -> None:
    from src.modding.utils import id_generator

    generated = id_generator.generate_id(ENTITY_PREFIX, 5)

    assert generated.startswith(ENTITY_PREFIX)
    assert len(generated) == len(ENTITY_PREFIX) + ENTITY_ID_LENGTH + 1
