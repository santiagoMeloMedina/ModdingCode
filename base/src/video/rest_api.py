import enum
from src.commons import entities
from singleton_injector import injector
from src.commons.http import HttpMethods
from src.video import stack as video_stack, lambdas as video_lambdas
from src.commons import security


class Scopes(enum.Enum):
    create_video = "create/video"
    get_video = "get/video"
    update_video = "update/video"
    delete_video = "delete/video"


@injector
class VideoRestApi(entities.LambdaRestApi):
    def __init__(
        self,
        scope: video_stack.VideoStack,
        add_video_lambda: video_lambdas.CreateVideoLambda,
        delete_video: video_lambdas.DeleteVideoLambda,
        update_video: video_lambdas.UpdateVideoLambda,
        get_video: video_lambdas.GetVideoLambda,
    ):
        api_id = "VideoRestApi"

        super().__init__(
            scope=scope,
            id=api_id,
            name=api_id,
            authorizer=security.Auth0Authorizer(scope, api_id),
        )

        self.main_resource = self.root.add_resource("video")

        self.add_method(
            resource=self.main_resource,
            method=HttpMethods.POST,
            integration_lambda=add_video_lambda,
            roles=[Scopes.create_video],
        )

        self.add_method(
            self.main_resource,
            method=HttpMethods.DELETE,
            integration_lambda=delete_video,
            roles=[Scopes.delete_video],
        )

        self.add_method(
            self.main_resource,
            method=HttpMethods.PUT,
            integration_lambda=update_video,
            roles=[Scopes.update_video],
        )

        self.get_video_resource = self.main_resource.add_resource("get")

        self.add_method(
            self.get_video_resource,
            method=HttpMethods.POST,
            integration_lambda=get_video,
            roles=[Scopes.get_video],
        )

        self.authorizer.construct_roles()
