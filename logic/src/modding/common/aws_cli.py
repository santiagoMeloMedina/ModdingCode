from typing import Any, Dict, List, Optional, Tuple
import boto3
from boto3.dynamodb.conditions import Key, Attr, ComparisonCondition


class AwsCustomClient:
    class S3:
        PUT_EXPIRE_TIME = 300

        def __init__(self, bucket_name: str):
            self.client = boto3.client("s3")
            self.bucket_name = bucket_name

        def put_file_presigned_url(self, object_name: str, expire: int) -> str:
            result = self.client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_name,
                    "ContentType": "binary/octet-stream",
                    "Expires": expire,
                },
            )
            return result

        def get_file_presigned_url(self, object_name: str, expire: int) -> str:
            result = self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_name,
                },
                ExpiresIn=expire,
            )
            return result

    class DynamoDB:
        def __init__(self, table_name: str):
            self.resource = boto3.resource("dynamodb")
            self.table = self.resource.Table(table_name)

        def query_items(
            self, keys: Dict[str, Any], filters: Dict[str, Tuple[str, str]]
        ) -> Optional[Dict[str, Any]]:
            key_conditions = None
            filter_conditions = None
            for key in keys:
                value = keys[key]
                condition = Key(key).eq(value)
                if key_conditions:
                    key_conditions = key_conditions & condition
                else:
                    key_conditions = condition

            for filter in filters:
                comparison, value = filters[filter]
                operator: ComparisonCondition = getattr(Attr(filter), comparison)
                condition = operator(value)
                if filter_conditions:
                    filter_conditions &= condition
                else:
                    filter_conditions = condition

            params = {
                "KeyConditionExpression": key_conditions,
                "FilterExpression": filter_conditions,
            }

            return self.table.query(**params).get("Items") or None

        def get_item(
            self, keys: Dict[str, Any], filters: Dict[str, Tuple[str, str]]
        ) -> Optional[Dict[str, Any]]:
            response = self.query_items(keys, filters)
            return response[0] if response else None

        def get_item_no_filters(
            self, values: Dict[str, Any]
        ) -> Optional[Dict[str, Any]]:
            return self.table.get_item(Key=values).get("Item") or None

        def put_item(self, item: Dict[str, Any]) -> None:
            self.table.put_item(Item=item)

        def delete_item(self, key: Dict[str, Any]) -> None:
            self.table.delete_item(Key=key)

    @classmethod
    def s3(cls, bucket_name: str) -> S3:
        return cls.S3(bucket_name)

    @classmethod
    def dynamo(cls, table_name: str) -> DynamoDB:
        return cls.DynamoDB(table_name=table_name)
