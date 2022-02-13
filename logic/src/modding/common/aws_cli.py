from typing import Any, Callable, Dict, Optional, Tuple
import boto3
import json
from boto3.dynamodb.conditions import Key, Attr, ComparisonCondition
import pydantic
from modding.common import exception
from modding.utils import jwt


class AwsCustomClient:
    class ApiGateway:
        class NoAuthorizationHeader(exception.LoggingErrorException):
            def __init__(self):
                super().__init__("There was no authorization header on headers")

        class AGWEvent(pydantic.BaseModel):
            body: Dict[str, Any]
            headers: Dict[str, Any]

        REPO_ACTION = "repo"

        AUTH_HEADER_NAME = "Authorization"

        @classmethod
        def __parse_event(cls, event: Dict[str, Any]) -> AGWEvent:
            parsed = cls.AGWEvent(
                body=json.loads(event.get("body", "{}")),
                headers=event.get("headers", dict()),
            )
            return parsed

        @classmethod
        def __decode_header_auth_token(cls, headers: Dict[str, Any]) -> Dict[str, Any]:
            if cls.AUTH_HEADER_NAME in headers:
                auth_value = headers.get(cls.AUTH_HEADER_NAME)
                token = jwt.obtain_token_from_bearer(auth_value)
                return jwt.decode_hs256_token_no_verify(token)
            else:
                raise cls.NoAuthorizationHeader()

        @staticmethod
        def __set_username_on_repos(*repositories: Any, username: str):
            for repository in repositories:
                repository.set_username(username)

        @classmethod
        def include_repos_action(cls, *repositories: Any):
            ### This is an action method to set username from token
            ### on repositories

            return {cls.REPO_ACTION: repositories}

        @classmethod
        def __token_actions(cls, headers: Dict[str, Any], **kwargs):
            ### This method will deal with the included decorated
            ### actions that need data from auth token

            actions = {cls.REPO_ACTION: cls.__set_username_on_repos}

            if any([key in actions for key in kwargs]):
                payload = cls.__decode_header_auth_token(headers)

                def dummy_method(*args, **kwargs):
                    pass

                for key in kwargs:
                    actions.get(key, dummy_method)(*kwargs.get(key), **payload)

        @classmethod
        def pre_handler(
            cls, handler: Callable[[Dict[str, Any], Dict[str, Any]], Any]
        ) -> Any:
            ## This decorator method will take the handle and use the parsed
            ## apigateway event for different actions like injecting data from
            ## events on different objects.

            def wrapper(*args, **kwargs) -> Any:
                parsed_event = cls.__parse_event(args[0])

                cls.__token_actions(parsed_event.headers, **kwargs)

                handled = handler(parsed_event, args[1])
                return handled

            return wrapper

    class S3:
        PUT_EXPIRE_TIME = 300

        def __init__(self, bucket_name: str):
            self.client = boto3.client("s3")
            self.bucket_name = bucket_name

        def put_file_presigned_url(self, object_name: str, expire: int) -> str:
            result = self.client.generate_presigned_url(
                ClientMethod="put_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_name,
                    "ContentType": "binary/octet-stream",
                    "Expires": expire,
                },
            )
            return result

        def get_file_presigned_url(self, object_name: str, expire: int) -> str:
            result = self.client.generate_presigned_url(
                ClientMethod="get_object",
                Params={
                    "Bucket": self.bucket_name,
                    "Key": object_name,
                },
                ExpiresIn=expire,
            )
            return result

    class DynamoDB:
        def __init__(self, table_name: str):
            self.resource = boto3.resource("dynamodb")
            self.table = self.resource.Table(table_name)

        def query_items(
            self, keys: Dict[str, Any], filters: Dict[str, Tuple[str, str]]
        ) -> Optional[Dict[str, Any]]:
            key_conditions = None
            filter_conditions = None
            for key in keys:
                value = keys[key]
                condition = Key(key).eq(value)
                if key_conditions:
                    key_conditions = key_conditions & condition
                else:
                    key_conditions = condition

            for filter in filters:
                comparison, value = filters[filter]
                operator: ComparisonCondition = getattr(Attr(filter), comparison)
                condition = operator(value)
                if filter_conditions:
                    filter_conditions &= condition
                else:
                    filter_conditions = condition

            params = {
                "KeyConditionExpression": key_conditions,
                "FilterExpression": filter_conditions,
            }

            return self.table.query(**params).get("Items") or None

        def scan_items(
            self, filters: Dict[str, Tuple[str, str]]
        ) -> Optional[Dict[str, Any]]:
            filter_conditions = None
            for filter in filters:
                comparison, value = filters[filter]
                operator: ComparisonCondition = getattr(Attr(filter), comparison)
                condition = operator(value)
                if filter_conditions:
                    filter_conditions &= condition
                else:
                    filter_conditions = condition

            return (
                self.table.scan(FilterExpression=filter_conditions).get("Items") or None
            )

        def get_item(
            self, keys: Dict[str, Any], filters: Dict[str, Tuple[str, str]]
        ) -> Optional[Dict[str, Any]]:
            response = self.query_items(keys, filters)
            return response[0] if response else None

        def get_item_no_filters(
            self, values: Dict[str, Any]
        ) -> Optional[Dict[str, Any]]:
            return self.table.get_item(Key=values).get("Item") or None

        def put_item(self, item: Dict[str, Any]) -> None:
            self.table.put_item(Item=item)

        def delete_item(self, key: Dict[str, Any]) -> None:
            self.table.delete_item(Key=key)

    @classmethod
    def s3(cls, bucket_name: str) -> S3:
        return cls.S3(bucket_name)

    @classmethod
    def dynamo(cls, table_name: str) -> DynamoDB:
        return cls.DynamoDB(table_name=table_name)
