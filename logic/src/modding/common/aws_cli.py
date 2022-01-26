from typing import Any, Dict
import boto3


class AwsCustomClient:
    class __S3:
        PUT_EXPIRE_TIME = 300

        def __init__(self):
            self.client = boto3.client("s3")

        def put_presigned_url(self, bucket_name: str, object_name: str) -> str:
            result = self.client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": bucket_name,
                    "Key": object_name,
                    "ContentType": "binary/octet-stream",
                    "Expires": self.PUT_EXPIRE_TIME,
                },
            )
            return result

    class __DynamoDB:
        def __init__(self, table_name: str):
            self.resource = boto3.resource("dynamodb")
            self.table = self.resource.Table(table_name)

        def put_item(self, item: Dict[str, Any]) -> None:
            self.table.put_item(Item=item)

        def delete_item(self, key: Dict[str, Any]) -> None:
            self.table.delete_item(Key=key)

    @classmethod
    def s3(cls) -> __S3:
        return cls.__S3()

    @classmethod
    def dynamo(cls, table_name: str) -> __DynamoDB:
        return cls.__DynamoDB(table_name=table_name)
