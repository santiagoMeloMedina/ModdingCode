from src.commons import entities
from singleton_injector import injector
from src.video import stack as video_stack

VIDEO_ROUTE = lambda name: f"/video/create/{name}"


@injector
class CreateVideoUrlExpirationTimeParam(entities.StringParam):
    def __init__(self, scope: video_stack.VideoStack):
        super().__init__(
            scope=scope,
            id="CreateVideoUrlExpirationTimeParam",
            path=VIDEO_ROUTE("upload-url-expiration-time"),
            value="300",
            env_name="UPLOAD_EXPIRE_TIME",
        )
