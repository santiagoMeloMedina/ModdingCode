from typing import Any, Dict
from modding.common import aws_cli, exception


class VideoRepository:
    class S3PresigningError(exception.LoggingErrorException):
        def __init__(self, message: str):
            super().__init__("Can not get presigned url, %s" % (message))

    def __init__(self, table_name: str, bucket_name: str):
        self.s3 = aws_cli.AwsCustomClient.s3()
        self.dynamo = aws_cli.AwsCustomClient.dynamo(table_name)
        self.bucket_name = bucket_name
        self.table_name = table_name

    def get_video_bucket_presigned_url(self, video_id: str) -> str:
        try:
            put_url = self.s3.put_presigned_url(
                bucket_name=self.bucket_name,
                object_name=video_id,
            )
        except Exception as e:
            raise VideoRepository.S3PresigningError(e)
        return put_url

    def save_video_data(self, data: Dict[str, Any]) -> None:
        self.dynamo.put_item(data)
