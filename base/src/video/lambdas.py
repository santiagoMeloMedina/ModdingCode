from src import stacks, lambdas
from singleton_injector import injector
from src.video import storage


@injector
class CreateVideoLambda(lambdas.LocalLambda):
    def __init__(
        self,
        scope: stacks.VideoStack,
        video_bucket: storage.VideosBucket,
    ):
        super().__init__(
            scope=scope,
            id="CreateVideoLambda",
            source="modding/video/create_video",
            env={"VIDEO_BUCKET_NAME": video_bucket.bucket_name},
        )

        video_bucket.grant_read_write(self)
