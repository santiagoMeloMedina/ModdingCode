from typing import Tuple
import pytest

ENTITY_PREFIX = "prefix"
ENTITY_ID_LENGTH = 5


@pytest.mark.unit
def test_id_generator() -> None:
    from src.modding.utils import id_generator

    generated = id_generator.generate_id(ENTITY_PREFIX, 5)

    assert generated.startswith(ENTITY_PREFIX)
    assert len(generated) == len(ENTITY_PREFIX) + ENTITY_ID_LENGTH + 1


@pytest.mark.unit
def test_retrier_with_generator() -> None:
    from src.modding.utils import id_generator

    PREFIX = "mock"
    MOCK_ATTR = "mock_name"

    def mock_create(id: str, mock_attr: str):
        return (id, mock_attr)

    generated: Tuple[str, str] = id_generator.retrier_with_generator(
        PREFIX, 5, func=mock_create, params=([], {"mock_attr": MOCK_ATTR}), tries=1
    )

    mock_id, mock_attr = generated

    assert mock_id.startswith(PREFIX)
    assert len(mock_id) == len(PREFIX) + 5 + mock_id.count("-")
    assert MOCK_ATTR == mock_attr
