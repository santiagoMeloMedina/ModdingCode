from typing import Any, Dict, List, Optional
import boto3


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

        def get_item(self, values: Dict[str, Any]) -> Optional[Dict[str, Any]]:
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
