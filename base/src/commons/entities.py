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
        self.index_names = dict()

    def get_env_name_var(self) -> Dict[str, Any]:
        separated = "_".join(re.findall("[A-Z][^A-Z]*", self.entity_name))
        return {f"{separated.upper()}_TABLE_NAME": self.table_name}

    def get_index_names(self) -> Dict[str, Any]:
        result = dict()
        for name in self.index_names:
            separated = "_".join(re.findall("[A-Z][^A-Z]*", name))
            result[f"{separated.upper()}_INDEX_NAME"] = self.index_names[name]
        return result

    def add_secundary_index(
        self,
        name: str,
        partition_key: _dynamodb.Attribute,
        sort_key: _dynamodb.Attribute = None,
    ) -> None:
        index_name = (
            f"{partition_key.name}{f'_{sort_key.name}' if sort_key else ''}_index"
        )
        self.add_global_secondary_index(
            index_name=index_name, partition_key=partition_key, sort_key=sort_key
        )
        self.index_names[name] = index_name


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


class SecureStringParam(_ssm.StringParameter):

    SECURE_PREFIX = "_secure_"

    def __init__(self, scope: Any, id: str, path: str, env_name: str):
        super().__init__(
            scope=scope,
            id=id,
            type=_ssm.ParameterType.STRING,  # TODO(Santiago): Must be secure and not createable
            parameter_name=path,
            string_value="temp",
        )

        self.path = "%s%s" % (self.SECURE_PREFIX, path)
        self.env_name = env_name


######################################
##             LAMBDA               ##
######################################


class Lambda(_lambda.Function):
    def __init__(
        self,
        scope: Stack,
        id: str,
        source: str,
        env: Dict[str, str],
        timeout_seconds: int = None,
    ):
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
            timeout=core.Duration.seconds(timeout_seconds) if timeout_seconds else None,
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

    def grant_param(
        self, param: _ssm.StringListParameter, read: bool = False, write: bool = False
    ) -> None:
        if read and write:
            param.grant_read(self)
            param.grant_write(self)
        elif read:
            param.grant_read(self)
        else:
            param.grant_write(self)


class Layer(_lambda.LayerVersion):
    def __init__(self, scope: Any):
        super().__init__(
            scope=scope,
            id="CommonLayer",
            code=_lambda.Code.from_asset(app_conf.LOGIC_LIBS_PATH),
            compatible_runtimes=[_lambda.Runtime.PYTHON_3_8],
        )


######################################
##            AUTHORIZERS           ##
######################################


class CustomLambdaAuthorizer(_apigateway.TokenAuthorizer):
    def __init__(self, scope: core.Stack, api_id: str, authorizer_lambda: Lambda):
        super().__init__(
            scope=scope, id="%s_authorizer" % (api_id), handler=authorizer_lambda
        )


######################################
##             RESTAPI              ##
######################################


class LambdaRestApi(_apigateway.RestApi):
    def __init__(
        self, scope: Any, id: str, name: str, authorizer: CustomLambdaAuthorizer = None
    ):
        super().__init__(scope=scope, id=id, rest_api_name=name)

        self.authorizer = authorizer

        self.authorizer_type = (
            _apigateway.AuthorizationType.CUSTOM if authorizer else None
        )

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
            authorization_type=self.authorizer_type,
            authorizer=self.authorizer,
        )


class LambdaApiIntegration(_apigateway.LambdaIntegration):
    def __init__(self, handler: Lambda):
        super().__init__(handler=handler)
