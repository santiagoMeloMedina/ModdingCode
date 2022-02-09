from unittest.mock import Mock, patch
import pytest


@pytest.mark.disable_aws_mock
@patch("modding.common.aws_cli.AwsCustomClient.DynamoDB.get_item")
def test_get_item_by_id(get_item: Mock) -> None:
    from modding.common import repo as subject, model

    class CustomEntity(model.Model):
        name: str

    class CustomEntityRepo(subject.Repository):
        def __init__(self):
            super().__init__(
                name="entity", table_name="entity_table", bucket_name="entity_bucket"
            )
            self.set_model(CustomEntity)

    MOCK_ENTITY_ID = "prefix-123"
    MOCK_ENTITY_NAME = "entity"

    mock_entity = CustomEntity(id=MOCK_ENTITY_ID, name=MOCK_ENTITY_NAME)

    mock_custom_entity_repo = CustomEntityRepo()
    get_item.return_value = mock_entity.dict()

    item_retrieved = mock_custom_entity_repo.get_item_by_id(MOCK_ENTITY_ID)

    assert item_retrieved == mock_entity


@pytest.mark.disable_aws_mock
@patch("modding.common.aws_cli.AwsCustomClient.DynamoDB.get_item")
def test_get_item_by_id_not_found(get_item: Mock) -> None:
    from modding.common import repo as subject, model

    class CustomEntity(model.Model):
        name: str

    class CustomEntityRepo(subject.Repository):
        def __init__(self):
            super().__init__(
                name="entity", table_name="entity_table", bucket_name="entity_bucket"
            )
            self.set_model(CustomEntity)

    MOCK_ENTITY_ID = "prefix-123"

    mock_custom_entity_repo = CustomEntityRepo()
    get_item.return_value = None

    with pytest.raises(subject.Repository._NotFoundEntityException):
        item_retrieved = mock_custom_entity_repo.get_item_by_id(MOCK_ENTITY_ID)
