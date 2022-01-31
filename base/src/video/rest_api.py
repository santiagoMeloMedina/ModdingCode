from src.commons import entities
from singleton_injector import injector
from src.commons.http import HttpMethods
from src.video import stack as video_stack, lambdas as video_lambdas


@injector
class VideoRestApi(entities.LambdaRestApi):
    def __init__(
        self,
        scope: video_stack.VideoStack,
        add_video_lambda: video_lambdas.CreateVideoLambda,
    ):
        super().__init__(scope=scope, id="VideoRestApi", name="VideoRestApi")

        self.main_resource = self.root.add_resource("video")

        self.add_method(
            resource=self.main_resource,
            method=HttpMethods.POST,
            integration_lambda=add_video_lambda,
        )
