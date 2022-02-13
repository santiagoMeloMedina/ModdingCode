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


@injector
class DeleteVideoLambda(entities.Lambda):
    def __init__(
        self,
        scope: video_stack.VideoStack,
        video_table: video_storage.VideoTable,
    ):
        super().__init__(
            scope=scope,
            id="DeleteVideoLambda",
            source="modding/video/delete_video",
            env={
                **video_table.get_env_name_var(),
            },
        )

        self.grant_table(video_table, read=True, write=True)


@injector
class UpdateVideoLambda(entities.Lambda):
    def __init__(
        self,
        scope: video_stack.VideoStack,
        video_table: video_storage.VideoTable,
    ):
        super().__init__(
            scope=scope,
            id="UpdateVideoLambda",
            source="modding/video/update_video",
            env={
                **video_table.get_env_name_var(),
            },
        )

        self.grant_table(video_table, read=True, write=True)


@injector
class GetVideoLambda(entities.Lambda):
    def __init__(
        self,
        scope: video_stack.VideoStack,
        video_bucket: video_storage.VideoBucket,
        video_table: video_storage.VideoTable,
    ):
        super().__init__(
            scope=scope,
            id="GetVideoLambda",
            source="modding/video/get_video",
            env={
                **video_table.get_env_name_var(),
                **video_bucket.get_env_name_var(),
                **video_table.get_index_names(),
                "VIDEO_DOWNLOAD_EXPIRE_TIME": "300",
            },
        )

        self.grant_table(video_table, read=True, write=True)
        self.grant_bucket(video_bucket, read=True, write=True)
