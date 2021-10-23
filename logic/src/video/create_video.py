from typing import Any, Dict
from src.common import logging, aws_cli, settings


class _Settings(settings.Settings):
    video_bucket_name: str


_SETTINGS = _Settings()
_LOGGER = logging.Logger()


def handler(event: Dict[str, Any], context: Any) -> None:
    s3 = aws_cli.AwsCli.s3()
    put_url = s3.put_presigned_url(
        bucket_name=_SETTINGS.video_bucket_name,
        object_name=event["body"]["video_name"],
    )

    _LOGGER.info(put_url)
