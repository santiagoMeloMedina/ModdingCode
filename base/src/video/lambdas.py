from src.commons import entities
from singleton_injector import injector
from src.video import stack as video_stack, storage as video_storage


@injector
class CreateVideoLambda(entities.Lambda):
    def __init__(
        self,
        scope: video_stack.VideoStack,
        video_bucket: video_storage.VideosBucket,
    ):
        super().__init__(
            scope=scope,
            id="CreateVideoLambda",
            source="modding/video/create_video",
            env={"VIDEO_BUCKET_NAME": video_bucket.bucket_name},
        )

        video_bucket.grant_read_write(self)
