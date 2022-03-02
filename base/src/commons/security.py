from typing import List
from src.commons import entities


class Auth0SignedCertificateParam(entities.SecureStringParam):
    def __init__(self, scope: entities.Stack, api_id: str):
        super().__init__(
            scope=scope,
            id="%s_Auth0SignedCertificateParam" % (api_id),
            path="/%s/auth0/signed_certificate" % (api_id),
            env_name="SIGNED_CERTIFICATE",
        )


class Auth0APIAudienceParam(entities.SecureStringParam):
    def __init__(self, scope: entities.Stack, api_id: str):
        super().__init__(
            scope=scope,
            id="%s_Auth0APIAudienceParam" % (api_id),
            path="/%s/auth0/api_audience" % (api_id),
            env_name="API_AUDIENCE",
        )


class Auth0AuthorizerRolesParam(entities.ConstructableSecureStringParam):
    def __init__(self, scope: entities.Stack, api_id: str):
        super().__init__(
            scope=scope,
            id="%s_Auth0AuthorizerRolesParam" % (api_id),
            path="/%s/auth0/authorizer_roles" % (api_id),
            env_name="AUTHORIZER_ROLES",
        )


class Auth0AuthorizerLambda(entities.Lambda):
    def __init__(
        self, scope: entities.Stack, api_id: str, roles_param: Auth0AuthorizerRolesParam
    ):

        signed_certificate = Auth0SignedCertificateParam(scope, api_id=api_id)
        api_audience = Auth0APIAudienceParam(scope, api_id=api_id)

        super().__init__(
            scope=scope,
            id="%s_Auth0AuthorizerLambda" % (api_id),
            source="modding/common/auth0/authorizer",
            env={
                signed_certificate.env_name: signed_certificate.path,
                api_audience.env_name: api_audience.path,
                roles_param.env_name: roles_param.path,
            },
        )

        self.grant_param(signed_certificate, read=True)
        self.grant_param(api_audience, read=True)
        self.grant_param(roles_param, read=True)


class Auth0Authorizer(entities.CustomLambdaAuthorizer):
    def __init__(self, scope: entities.Stack, api_id: str):

        self.authorizer_roles_param = Auth0AuthorizerRolesParam(
            scope=scope, api_id=api_id
        )
        self.authorizer_lambda = Auth0AuthorizerLambda(
            scope=scope, api_id=api_id, roles_param=self.authorizer_roles_param
        )

        super().__init__(
            scope=scope,
            api_id="AllApiAuth0Authorizer",
            authorizer_lambda=self.authorizer_lambda,
        )

    def add_role(self, method_arn: str, roles: List[str]):
        lambda_roles = "%s:%s" % (method_arn, ",".join(roles))
        self.authorizer_roles_param.add_to_value(lambda_roles)

    def construct_roles(self):
        self.authorizer_roles_param.construct_secure_string()
