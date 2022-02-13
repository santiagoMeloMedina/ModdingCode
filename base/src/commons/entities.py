import re

from typing import Any, Dict, Optional
from aws_cdk import (
    core,
    aws_lambda as _lambda,
    aws_s3 as _s3,
    aws_dynamodb as _dynamodb,
    aws_apigateway as _apigateway,
    aws_iam as _iam,
    aws_ssm as _ssm,
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

        self.layer = Layer(scope=self)


######################################
##            DYNAMODB              ##
######################################


class Table(_dynamodb.Table):
    def __init__(
        self,
        scope: core.Stack,
        entity_name: str,
        partition_key: _dynamodb.Attribute,
        sort_key: Optional[_dynamodb.Attribute] = _dynamodb.Attribute(
            name="username", type=_dynamodb.AttributeType.STRING
        ),
    ):
        super().__init__(
            scope=scope,
            id=f"{entity_name}Table",
            table_name=f"{scope.stack_name}_{entity_name}",
            partition_key=partition_key,
            sort_key=sort_key,
            billing_mode=_dynamodb.BillingMode.PAY_PER_REQUEST,
            stream=_dynamodb.StreamViewType.NEW_AND_OLD_IMAGES,
            removal_policy=core.RemovalPolicy.DESTROY,
        )
        self.entity_name = entity_name

    def get_env_name_var(self) -> Dict[str, Any]:
        separated = "_".join(re.findall("[A-Z][^A-Z]*", self.entity_name))
        return {f"{separated.upper()}_TABLE_NAME": self.table_name}

    def add_secundary_index(
        self, partition_key: _dynamodb.Attribute, sort_key: _dynamodb.Attribute = None
    ) -> None:
        index_name = (
            f"{partition_key.name}{f'_{sort_key.name}' if sort_key else ''}_index"
        )
        self.add_global_secondary_index(
            index_name=index_name, partition_key=partition_key, sort_key=sort_key
        )


######################################
##            S3 BUCKET             ##
######################################


class Bucket(_s3.Bucket):
    def __init__(self, scope: core.Stack, id: str, entity_name: str):
        super().__init__(scope=scope, id=id, removal_policy=core.RemovalPolicy.DESTROY)
        self.entity_name = entity_name

    def get_env_name_var(self) -> Dict[str, Any]:
        return {f"{self.entity_name.upper()}_BUCKET_NAME": self.bucket_name}


######################################
##             LAMBDA               ##
######################################


class Lambda(_lambda.Function):
    def __init__(self, scope: Stack, id: str, source: str, env: Dict[str, str]):
        super().__init__(
            scope=scope,
            id=id,
            code=_lambda.Code.from_asset(
                app_conf.LOGIC_SRC_PATH,
                exclude=app_conf.get_excluded_files_from_logic(
                    source, scope.stack_name
                ),
            ),
            handler=".".join([source, "handler"]),
            runtime=_lambda.Runtime.PYTHON_3_8,
            environment=env,
            layers=[scope.layer],
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
##              PARAMS              ##
######################################


class StringParam(_ssm.StringParameter):
    def __init__(self, scope: Any, id: str, path: str, value: str, env_name: str):
        super().__init__(
            scope=scope,
            id=id,
            type=_ssm.ParameterType.STRING,
            parameter_name=path,
            string_value=value,
        )

        self.env_name = env_name


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
