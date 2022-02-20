from src.commons import entities


class Auth0SignedCertificateParam(entities.SecureStringParam):
    def __init__(self, scope: entities.Stack, api_id: str):
        super().__init__(
            scope=scope,
            id="%s_Auth0SignedCertificateParam" % (api_id),
            path="/auth0/signed_certificate",
            env_name="SIGNED_CERTIFICATE",
        )


class Auth0APIAudienceParam(entities.SecureStringParam):
    def __init__(self, scope: entities.Stack, api_id: str):
        super().__init__(
            scope=scope,
            id="%s_Auth0APIAudienceParam" % (api_id),
            path="/auth0/api_audience",
            env_name="API_AUDIENCE",
        )


class Auth0AuthorizerLambda(entities.Lambda):
    def __init__(self, scope: entities.Stack, api_id: str):

        signed_certificate = Auth0SignedCertificateParam(scope, api_id=api_id)
        api_audience = Auth0APIAudienceParam(scope, api_id=api_id)

        super().__init__(
            scope=scope,
            id="%s_Auth0AuthorizerLambda" % (api_id),
            source="modding/common/auth0/authorizer",
            env={
                signed_certificate.env_name: signed_certificate.path,
                api_audience.env_name: api_audience.path,
            },
        )

        self.grant_param(signed_certificate, read=True)
        self.grant_param(api_audience, read=True)


class Auth0Authorizer(entities.CustomLambdaAuthorizer):
    def __init__(self, scope: entities.Stack, api_id: str):

        authorizer_lambda = Auth0AuthorizerLambda(scope=scope, api_id=api_id)

        super().__init__(
            scope=scope,
            api_id="AllApiAuth0Authorizer",
            authorizer_lambda=authorizer_lambda,
        )
