import boto3


class _S3:

    PUT_EXPIRE_TIME = 120

    def __init__(self):
        self.client = boto3.client("s3")

    def put_presigned_url(self, bucket_name: str, object_name: str) -> str:
        result = self.client.generate_presigned_url(
            ClientMethod="put_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=self.PUT_EXPIRE_TIME,
        )
        return result


class AwsCli:
    def s3(self) -> _S3:
        return _S3()
