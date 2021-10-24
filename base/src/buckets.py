from aws_cdk import aws_s3 as _s3, core


class Bucket(_s3.Bucket):
    def __init__(
        self,
        scope: core.Stack,
        id: str,
    ):
        super().__init__(scope=scope, id=id)
