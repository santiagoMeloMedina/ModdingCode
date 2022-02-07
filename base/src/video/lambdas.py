from src.commons import entities
from singleton_injector import injector
from src.video import (
    stack as video_stack,
    storage as video_storage,
    parameters as video_params,
)


@injector
class CreateVideoLambda(entities.Lambda):
    def __init__(
        self,
        scope: video_stack.VideoStack,
        video_bucket: video_storage.VideoBucket,
        video_table: video_storage.VideoTable,
        expiration_time: video_params.CreateVideoUrlExpirationTimeParam,
    ):
        super().__init__(
            scope=scope,
            id="CreateVideoLambda",
            source="modding/video/create_video",
            env={
                **video_table.get_env_name_var(),
                **video_bucket.get_env_name_var(),
                expiration_time.env_name: expiration_time.string_value,
            },
        )

        self.grant_table(video_table, read=True, write=True)
        self.grant_bucket(video_bucket, read=True, write=True)
