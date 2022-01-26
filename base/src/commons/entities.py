from types import MethodType
from typing import Any, Dict, Optional
from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_s3 as _s3,
    aws_dynamodb as _dynamodb,
    aws_apigateway as _apigateway,
    aws_iam as _iam,
)
import src.commons.conf as app_conf
from src.commons.http import HttpMethods


######################################
##              STACK               ##
######################################


class Stack(core.Stack):
    def __init__(self, id: str, name: str):
        super().__init__(
            scope=app_conf.app, id=id, stack_name=name, env=app_conf.environment
        )


######################################
##            DYNAMODB              ##
######################################


class Table(_dynamodb.Table):
    def __init__(
        self,
        scope: core.Stack,
        id: str,
        name: str,
        partition_key: _dynamodb.Attribute,
        sort_key: Optional[_dynamodb.Attribute] = None,
    ):
        super().__init__(
            scope=scope,
            id=id,
            table_name=name,
            partition_key=partition_key,
            sort_key=sort_key,
            billing_mode=_dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=_dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
        )


######################################
##            S3 BUCKET             ##
######################################


class Bucket(_s3.Bucket):
    def __init__(
        self,
        scope: core.Stack,
        id: str,
    ):
        super().__init__(scope=scope, id=id)


######################################
##             LAMBDA               ##
######################################


class Lambda(_lambda.Function):
    def __init__(self, scope: Any, id: str, source: str, env: Dict[str, str]):
        super().__init__(
            scope=scope,
            id=id,
            code=_lambda.Code.from_asset(app_conf.LOGIC_SRC_PATH),
            handler=".".join([source, "handler"]),
            runtime=_lambda.Runtime.PYTHON_3_8,
            environment=env,
            layers=[Layer(scope=scope)],
        )

    def grant_table(
        self, table: Table, read: bool = False, write: bool = False
    ) -> None:
        if read and write:
            table.grant_read_write_data(self)
        elif read:
            table.grant_read_data(self)
        else:
            table.grant_write_data(self)

    def grant_bucket(
        self, bucket: Bucket, read: bool = False, write: bool = False
    ) -> None:
        if read and write:
            bucket.grant_read_write(self)
        elif read:
            bucket.grant_read(self)
        else:
            bucket.grant_write(self)


class Layer(_lambda.LayerVersion):
    def __init__(self, scope: Any):
        super().__init__(
            scope=scope,
            id="CommonLayer",
            code=_lambda.Code.from_asset(app_conf.LOGIC_LIBS_PATH),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
        )


######################################
##             RESTAPI              ##
######################################


class LambdaRestApi(_apigateway.RestApi):
    def __init__(self, scope: Any, id: str, name: str):
        super().__init__(scope=scope, id=id, rest_api_name=name)

        self.authorizer = None

    def add_method(
        self,
        resource: _apigateway.Resource,
        method: HttpMethods,
        integration_lambda: Lambda,
    ) -> _apigateway.Method:
        lambda_integrated = LambdaApiIntegration(handler=integration_lambda)
        return resource.add_method(
            http_method=method.value,
            integration=lambda_integrated,
            authorizer=self.authorizer,
        )


class LambdaApiIntegration(_apigateway.LambdaIntegration):
    def __init__(self, handler: Lambda):
        super().__init__(handler=handler)
